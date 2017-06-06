import time
from itchat.content import *
from master_robot import Robot

FENQUN_HELP = '''回复【我要进群】进行下一步操作'''

FENQUN_AUTOREPLY = '''这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的免费共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

【1023】机械机电自动化交流群
【1024】金融行业交流群
【1025】IT互联网行业交流群
【1026】房产建筑行业交流群
【1027】快消零售交流群
【1028】广告媒体交流群
【1029】教育行业交流群
【1030】医疗行业交流群
【1031】电子电器行业交流群
【1032】交通运输物流交流群
【1033】化工行业交流群
【1034】冶炼五金交流群
【1035】能源资源交流群

回复行业群前面对应的4位数字，获取进群邀请。最多获取两次。

【入群必读】为了保证行业群群环境良好，进群后会有严格群规，请大家严格遵守。

【备注】如果以上细分群没有您感兴趣的，敬请等待第三期细分群邀请。'''


class FenqunRobot(Robot):

    def __init__(self, env, id, qrCallback):
        super().__init__(env=env, id=id, duty='partial robot', qrCallback=qrCallback)

        @self.robot.msg_register(TEXT)
        def keyword_reply(msg):
            '''
            用户回复数字，发送分群链接；否则，自动回复文案
            :param msg:
            :return:
            '''
            user_id = msg['FromUserName']
            user_remarkname = msg.User['RemarkName']
            user_nickname = msg.User['NickName']
            user_name = user_remarkname if user_remarkname else user_nickname
            if '我要进群' in msg['Text']:
                self.robot.send(FENQUN_AUTOREPLY, user_id)
            elif msg['Text'] in FenqunRobot.division_group_map.keys():
                client, db = self.connect_mongo()
                if client and db:
                    count = db.user.count({'name': user_name, 'is_fenqun_invited': {'$gte': 2}})
                    if count > 0:
                        self.robot.send('获取群邀请次数已达上限', user_id)
                        return

                ret = ''
                friend = self.robot.search_friends(name=user_name)
                chatrooms = self.robot.search_chatrooms(name=FenqunRobot.division_group_map.get(msg['Text']))
                if not friend:
                    friend = self.robot.search_friends(name=user_name)
                if not chatrooms:
                    chatrooms = self.robot.search_chatrooms(name=FenqunRobot.division_group_map.get(msg['Text']))
                if isinstance(friend, list) and len(friend)==1 and chatrooms:
                    ret = self.robot.add_member_into_chatroom(chatrooms[0]['UserName'], friend, useInvitation=True)
                    if ret:
                        group_tag_id = 'tags.g' + msg['Text']
                        stat_info = {
                            '$inc': {group_tag_id: 1},
                            '$set': {
                                'last_update': int(time.time())
                            }
                        }
                        self.do_stat(stat_info)
                        register_info = {
                            '$inc': {
                                'is_fenqun_invited': 1,
                                group_tag_id: 1
                            },
                            '$set': {
                                'is_fenqun_friend': 1,
                                'receive_robot': self.name,
                                'last_update': int(time.time())
                            }
                        }
                        self.do_register(user_name, register_info)
                print("friend->{}\nchatroom {}->{}\nret->{}\n".format(friend, FenqunRobot.division_group_map.get(msg['Text']), chatrooms, ret))
            else:
                self.robot.send(FENQUN_HELP, user_id)

        @self.robot.msg_register(FRIENDS)
        def add_friend(msg):
            '''
            自动加好友，并回复入群指示
            :param msg:
            :return:
            '''
            print(msg)
            self.robot.add_friend(userName=msg['RecommendInfo']['UserName'], status=3)
            alias = msg['RecommendInfo']['NickName']+'_'+str(int(time.time()))
            self.robot.set_alias(msg['RecommendInfo']['UserName'], alias)
            ret = self.robot.send(FENQUN_AUTOREPLY, msg['RecommendInfo']['UserName'])
            if ret:
                stat_info = {
                    '$inc': {'is_fenqun_friend': 1},
                    '$set': {
                        'last_update': int(time.time())
                    }
                }
                self.do_stat(stat_info)
                register_info = {
                    '$set': {
                        'is_fenqun_friend': 1,
                        'receive_robot': self.name,
                        'create_time': int(time.time()),
                        'last_update': int(time.time())
                    }
                }
                self.do_register(alias, register_info)