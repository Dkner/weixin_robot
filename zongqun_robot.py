import os
import time
import json
from random import choice
from itchat.content import *
from master_robot import Robot

ZONGQUN_HELP = '''回复【我要进群】进行下一步操作'''

ZONGQUN_AUTOREPLY = '''您好，我是名片全能王社群的群小蜜，请仔细阅读下方文字哦：

【入群必读】
这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

【进群门槛】
本社群不收取任何会费，所有服务皆免费，为了壮大我们的社群，有一个小小的请求，希望您将以下海报分享到朋友圈并截图发给我，我才会拉你入群哦！非常感谢您的配合。 

【分享如下海报到朋友圈】'''


class ZongqunRobot(Robot):
    def __init__(self, env, id, qrCallback):
        super().__init__(env=env, id=id, duty='central robot', qrCallback=qrCallback)
        self.command_func_dict = {}
        self.register_command()

        @self.robot.msg_register(TEXT)
        def admin_task(msg):
            '''
            接收机器人管理员的任务消息执行相应的任务
            :param msg:
            :return:
            '''
            sign = msg['Text'][:32]
            if sign != Robot.sign:
                return
            command = json.loads(msg['Text'][32:])
            command_func = self.command_func_dict.get(command['key'])
            if not command_func:
                return
            try:
                command_func(command['value'])
            except Exception as e:
                print(e)

        @self.robot.msg_register(TEXT)
        def keyword_reply(msg):
            '''
            关键词回复
            :param msg:
            :return:
            '''
            user_id = msg['FromUserName']
            user_remarkname = msg.User['RemarkName']
            user_nickname = msg.User['NickName']
            user_name = user_remarkname if user_remarkname else user_nickname
            register_info = {
                '$set': {
                    'is_zongqun_friend': 1,
                    'receive_robot': self.name,
                    'last_update': int(time.time())
                }
            }
            self.do_register(user_name, register_info)

            if '我要进群' in msg['Text']:
                self.robot.send(ZONGQUN_AUTOREPLY, user_id)
            else:
                self.robot.send(ZONGQUN_HELP, user_id)

        @self.robot.msg_register(PICTURE)
        def add_group_reply(msg):
            '''
            收到用户截图，发送总群链接
            :param msg:
            :return:
            '''
            user_remarkname = msg.User['RemarkName']
            user_nickname = msg.User['NickName']
            user_name = user_remarkname if user_remarkname else user_nickname
            self.group_invite(user_name)

        @self.robot.msg_register(FRIENDS)
        def add_friend(msg):
            '''
            1.自动加好友，并回复自我介绍和入群指示
            2.统计已加好友
            3.埋点24小时的群邀请任务
            :param msg:
            :return:
            '''
            print(msg)
            self.robot.add_friend(userName=msg['RecommendInfo']['UserName'], status=3)
            alias = msg['RecommendInfo']['NickName'] + '_' + str(int(time.time()))
            self.robot.set_alias(msg['RecommendInfo']['UserName'], alias)
            self.robot.send(ZONGQUN_AUTOREPLY, msg['RecommendInfo']['UserName'])
            ret = self.robot.send('@img@{}'.format(os.path.join(self.data_dir, choice(Robot.editor_pic))), msg['RecommendInfo']['UserName'])
            if ret:
                stat_info = {
                    '$inc': {'is_zongqun_friend': 1},
                    '$set': {
                        'last_update': int(time.time())
                    }
                }
                self.do_stat(stat_info)
                register_info = {
                    '$set': {
                        'is_zongqun_friend': 1,
                        'receive_robot': self.name,
                        'create_time': int(time.time()),
                        'last_update': int(time.time())
                    }
                }
                self.do_register(alias, register_info)
                self.add_group_invite_trigger(alias)

    def register_command(self):
        self.command_func_dict['group_invite'] = self.group_invite

    def group_invite(self, value):
        print('group_invite------------------',value)
        user = self.robot.search_friends(name=value)

        client, db = self.connect_mongo()
        if user and client and db:
            count = db.user.count({'name': value, 'is_zongqun_invited': {'$gt': 0}})
            if count>0:
                return

        ret = ''
        chatroom_id = choice(list(Robot.center_group.keys()))
        chatrooms = self.robot.search_chatrooms(name=Robot.center_group[chatroom_id])
        if not chatrooms:
            chatroom_id = choice(list(Robot.center_group.keys()))
            chatrooms = self.robot.search_chatrooms(name=Robot.center_group[chatroom_id])
        if isinstance(user, list) and len(user)==1 and chatrooms:
            ret = self.robot.add_member_into_chatroom(chatrooms[0]['UserName'], user, useInvitation=True)
        print("friend->{}\nchatroom {}->{}\nret->{}\n".format(user, chatroom_id, chatrooms, ret))
        if ret:
            group_tag_id = 'tags.g' + chatroom_id
            stat_info = {
                '$inc': {group_tag_id: 1},
                '$set': {
                    'last_update': int(time.time())
                }
            }
            self.do_stat(stat_info)
            register_info = {
                '$inc': {group_tag_id: 1},
                '$set': {
                    'is_zongqun_invited': 1,
                    'last_update': int(time.time())
                }
            }
            self.do_register(value, register_info)

    def add_group_invite_trigger(self, user_name):
        client, db = self.connect_mongo()
        if not client or not db:
            print('connect mongo failed')
            return False
        task_info = {
            'key': 'group_invite',
            'value': {
                'robot_name': self.name,
                'user_name': user_name,
            },
            'trigger_time': int(time.time()) + 86400,
            # 'trigger_time': int(time.time()),
            'status': 1
        }
        db.task.insert(task_info)