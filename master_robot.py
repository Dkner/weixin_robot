import json
import os
import platform
import threading
import time
from random import choice

import itchat
import pymongo
import redis
from itchat.content import *

from conf import config

HELP = '''你好！我是机器人管理员。
回复“总群机器人”——获取总群机器人的身份二维码
回复“分群机器人”——获取分群机器人的身份二维码

注意事项：
1）获取二维码之后扫描登录即可成为相应机器人
2）获取二维码后不登录超过一定时间，二维码会失效，若失效请重新操作
3）每个二维码只能供一个机器人使用
4）在微信中退出网页版登录即可退出机器人模式'''

ZONGQUN_AUTOREPLY = '''您好，我是名片全能王社群的群小蜜，请仔细阅读下方文字哦：

【入群必读】
这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

【进群门槛】
本社群不收取任何会费，所有服务皆免费，为了壮大我们的社群，有一个小小的请求，希望您将以下海报分享到朋友圈并截图发给我，我才会拉你入群哦！非常感谢您的配合。 

【分享如下海报到朋友圈】'''

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

回复行业群前面对应的4位数字，获取进群邀请。

【入群必读】为了保证行业群群环境良好，进群后会有严格群规，请大家严格遵守。

【备注】如果以上细分群没有您感兴趣的，敬请等待第三期细分群邀请。'''


class Robot(object):
    sign = '660d69e655f0a455c8c625584fd63470'
    division_group_map = {
        # '1023': '名片全能王 - 机械机电自动化交流群',
        # '1024': '名片全能王 - 金融行业交流群',
        # '1025': '名片全能王 - IT互联网行业交流群',
        # '1026': '名片全能王 - 房产建筑行业交流群',
        # '1027': '名片全能王 - 快消零售交流群',
        # '1028': '名片全能王 - 广告媒体交流群',
        # '1029': '名片全能王 - 教育行业交流群',
        # '1030': '名片全能王 - 医疗行业交流群',
        # '1031': '名片全能王 - 电子电器行业交流群',
        # '1032': '名片全能王 - 交通运输物流交流群',
        # '1033': '名片全能王 - 化工行业交流群',
        # '1034': '名片全能王 - 冶炼五金交流群',
        # '1035': '名片全能王 - 能源资源交流群',
        'fenqun1': '微信机器人开发'
    }
    # editor_pic = ['chenchen.png', 'miaomiao.png', 'nana.png', 'xiaofang.png', 'xiaoyi.png', 'xiaozhi.png']
    editor_pic = ['chenchen.png', 'xiaozhi.png']
    center_group = {
        # '3': '名片全能王3群-商务资源对接',
        # '19': '名片全能王19群-商务资源对接',
        # '20': '名片全能王20群-商务资源对接',
        'test1': 'CC微信机器人开发',
        'test2': 'CC微信机器人开发'
    }

    def __init__(self, env='DEV', id='robot_id', duty='robot', enableCmdQR=False, qrCallback=False, hotReload=False, blockThread=False):
        self.env = env
        if id=='robot_id':
            # self.id = 'robot_'+ str(int(time.time()))
            self.id = 'robot_id'
        else:
            self.id = id
        self.name = ''
        self.duty = duty
        self.data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'data')
        self.temp_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'temp')
        self.enableCmdQR = enableCmdQR
        self.hotReload = hotReload
        self.qrCallback = qrCallback
        self.blockThread = blockThread
        self.robot = itchat.new_instance()

    def connect_redis(self):
        connection = redis.Redis(host=config.REDIS[self.env]['host'], port=int(config.REDIS[self.env]['port']), db=int(
            config.REDIS[self.env]['db']),
                                 password=config.REDIS[self.env]['password'])
        return connection

    def connect_mongo(self):
        conn = pymongo.MongoClient(config.MONGO[self.env]['host'], int(config.MONGO[self.env]['port']))
        db = eval("conn." + config.MONGO[self.env]['db'])
        ret = db.authenticate(config.MONGO[self.env]['user'], config.MONGO[self.env]['password'], config.MONGO[self.env]['db'])
        if not ret:
            return conn, False
        return conn, db

    def do_stat(self, stat_info):
        client, db = self.connect_mongo()
        if not client or not db:
            print('connect mongo failed')
            return False
        db.stat.update_one({'date':'2017'}, stat_info, True)

    def do_register(self, name, register_info):
        if not name:
            return False
        client, db = self.connect_mongo()
        if not client or not db:
            print('connect mongo failed')
            return False
        db.user.update_many({'name':name}, register_info, True)

    def login_callback(self):
        self.id = self.robot.storageClass.userName
        self.name = self.robot.storageClass.nickName
        client, db = self.connect_mongo()
        if not client or not db:
            print('connect mongo failed')
            return False
        robot_info = {
            'id': self.id,
            'name': self.name,
            'status': 1,
            'duty': self.duty,
            'last_update': int(time.time())
        }
        db.robot.update_one({'name': self.name}, {'$set': robot_info}, True)

    def exit_callback(self):
        client, db = self.connect_mongo()
        if not client or not db:
            print('connect mongo failed')
            return False
        robot_info = {
            'status': 0,
            'last_update': int(time.time())
        }
        db.robot.update_one({'name': self.robot.storageClass.nickName}, {'$set': robot_info}, True)

    def run(self):
        self.robot.auto_login(hotReload=self.hotReload,
                              statusStorageDir=os.path.join(self.temp_dir, self.id+'.pkl'),
                              picDir=os.path.join(self.temp_dir, self.id+'.png'),
                              enableCmdQR=self.enableCmdQR,
                              qrCallback=self.qrCallback,
                              loginCallback=self.login_callback,
                              exitCallback=self.exit_callback)
        self.robot.run(debug=True, blockThread=self.blockThread)


class RobotAdmin(Robot):

    def __init__(self, env):
        enableCmdQR = 2 if 'Linux' in platform.platform() else False
        super(RobotAdmin, self).__init__(env=env, duty='robot admin', enableCmdQR=enableCmdQR, blockThread=True, hotReload=True)
        self.QR_MAX_TRIED_COUNT = 0
        self.command_func_dict = {}
        self.register_command()
        self.command_reply()

        @self.robot.msg_register(TEXT)
        def text_reply(msg):
            print(msg)
            self.QR_MAX_TRIED_COUNT = 0

            def add_editor_qr_callback(uuid, status, qrcode):
                if self.QR_MAX_TRIED_COUNT<2:
                    pic_file = os.path.join(self.temp_dir, msg['FromUserName'] + '.png')
                    with open(pic_file, 'wb') as f:
                        f.write(qrcode)
                    self.robot.send('Please scan the QR code to log in.', msg['FromUserName'])
                    self.robot.send('@img@{}'.format(pic_file), msg['FromUserName'])
                elif self.QR_MAX_TRIED_COUNT>5 or str(status)=='408':
                    self.robot.send('Scan timeout, Please request again', msg['FromUserName'])
                    exit(0)
                self.QR_MAX_TRIED_COUNT += 1

            if '总群机器人' in msg['Text']:
                editor = ZongqunRobot(env=self.env, id=msg['FromUserName'], qrCallback=add_editor_qr_callback)
                editor.run()
                self.robot.send('login in as central robot success', msg['FromUserName'])
            elif '分群机器人' in msg['Text']:
                editor = FenqunRobot(env=self.env, id=msg['FromUserName'], qrCallback=add_editor_qr_callback)
                editor.run()
                self.robot.send('login in as partial robot success', msg['FromUserName'])
            elif '使用说明' in msg['Text']:
                self.robot.send(HELP, msg['FromUserName'])

    def register_command(self):
        self.command_func_dict['group_invite'] = self.group_invite

    def group_invite(self, value):
        editor_robot = self.robot.search_friends(nickName=value['robot_name'])
        print(editor_robot)
        if editor_robot:
            command = {
                'key': 'group_invite',
                'value': value['user_name']
            }
            command = Robot.sign + json.dumps(command)
            self.robot.send(command, editor_robot[0]['UserName'])

    def command_reply(self):
        def maintain_loop():
            redis = self.connect_redis()
            while True:
                data = redis.blpop('weixin_robot_admin_command', timeout=1)
                if not data:
                    continue
                command = json.loads(data[1].decode('utf-8'))
                print(command)
                try:
                    command_func = self.command_func_dict.get(command['key'])
                    if not command_func:
                        continue
                    command_func(command['value'])
                except Exception as e:
                    print(e)

        maintain_thread = threading.Thread(target=maintain_loop)
        maintain_thread.setDaemon(True)
        maintain_thread.start()


class FenqunRobot(Robot):

    def __init__(self, env, id, qrCallback):
        super(FenqunRobot, self).__init__(env=env, id=id, duty='partial robot', hotReload=True, qrCallback=qrCallback)

        @self.robot.msg_register(TEXT)
        def auto_reply(msg):
            '''
            用户回复数字，发送分群链接；否则，自动回复文案
            :param msg:
            :return:
            '''
            if msg['Text'] in FenqunRobot.division_group_map.keys():
                client, db = self.connect_mongo()
                if client and db:
                    count = db.user.count({'name': msg.User['RemarkName'], 'is_fenqun_invited': {'$gt': 2}})
                    if count > 0:
                        self.robot.send('获取群邀请次数已达上限', msg['FromUserName'])
                        return

                ret = ''
                friend = self.robot.search_friends(name=msg.User['RemarkName'])
                chatrooms = self.robot.search_chatrooms(name=FenqunRobot.division_group_map.get(msg['Text']))
                if not friend:
                    friend = self.robot.search_friends(name=msg.User['RemarkName'])
                if not chatrooms:
                    chatrooms = self.robot.search_chatrooms(name=FenqunRobot.division_group_map.get(msg['Text']))
                if isinstance(friend, dict) and len(friend)==1 and chatrooms:
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
                                'last_update': int(time.time())
                            }
                        }
                        self.do_register(msg.User['RemarkName'], register_info)
                print("friend->{}\nchatroom {}->{}\nret->{}".format(friend, FenqunRobot.division_group_map.get(msg['Text']), chatrooms, ret))
            else:
                self.robot.send(FENQUN_AUTOREPLY, msg['FromUserName'])

        @self.robot.msg_register(FRIENDS)
        def add_friend(msg):
            '''
            自动加好友，并回复入群指示
            :param msg:
            :return:
            '''
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
                        'is_zongqun_friend': 1,
                        'receive_robot': self.name,
                        'create_time': int(time.time()),
                        'last_update': int(time.time())
                    }
                }
                self.do_register(alias, register_info)


class ZongqunRobot(Robot):
    def __init__(self, env, id, qrCallback):
        super(ZongqunRobot, self).__init__(env=env, id=id, duty='central robot', hotReload=True, qrCallback=qrCallback)
        self.command_func_dict = {}
        self.register_command()

        @self.robot.msg_register(TEXT)
        def admin_task(msg):
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

        @self.robot.msg_register(PICTURE)
        def add_group_reply(msg):
            '''
            收到用户截图，发送总群链接
            :param msg:
            :return:
            '''
            print(msg)
            self.group_invite(msg.User['RemarkName'])

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
                # self.robot.send('获取群邀请次数已达上限', user[0]['UserName'])
                return

        ret = ''
        chatroom_id = choice(list(Robot.center_group.keys()))
        chatrooms = self.robot.search_chatrooms(name=Robot.center_group[chatroom_id])
        if not chatrooms:
            chatroom_id = choice(list(Robot.center_group.keys()))
            chatrooms = self.robot.search_chatrooms(name=Robot.center_group[chatroom_id])
        if isinstance(user, dict) and len(user)==1 and chatrooms:
            # ret = self.robot.add_member_into_chatroom(chatrooms[0]['UserName'], user, useInvitation=True)
            print('shit--------------')
        print("friend->{}\nchatroom {}->{}\nret->{}".format(user, chatroom_id, chatrooms, ret))
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
                'create_time': int(time.time()),
                'trigger_time': int(time.time()) + 86400
            }
        }
        db.task.insert(task_info)