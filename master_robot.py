import json
import os
import platform
import threading
import time

import itchat
import pymongo
import redis
from itchat.content import *
from conf import config
from fenqun_robot import FenqunRobot
from zongqun_robot import ZongqunRobot

HELP = '''你好！我是机器人管理员。
回复“总群机器人”——获取总群机器人的身份二维码
回复“分群机器人”——获取分群机器人的身份二维码

注意事项：
1）获取二维码之后扫描登录即可成为相应机器人
2）获取二维码后不登录超过一定时间，二维码会失效，若失效请重新操作
3）每个二维码只能供一个机器人使用
4）在微信中退出网页版登录即可退出机器人模式'''


class Robot(object):
    sign = '660d69e655f0a455c8c625584fd63470'
    division_group_map = {
        '1023': '名片全能王-机械机电自动化交流群',
        '1024': '名片全能王-金融行业交流群',
        '1025': '名片全能王-IT互联网行业交流群',
        '1026': '名片全能王-房产建筑行业交流群',
        '1027': '名片全能王-快消零售交流群',
        '1028': '名片全能王-广告媒体交流群',
        '1029': '名片全能王-教育行业交流群',
        '1030': '名片全能王-医疗行业交流群',
        '1031': '名片全能王-电子电器行业交流群',
        '1032': '名片全能王-交通运输物流交流群',
        '1033': '名片全能王-化工行业交流群',
        '1034': '名片全能王-冶炼五金交流群',
        '1035': '名片全能王-能源资源交流群',
        # 'fenqun1': '微信机器人开发'
    }
    # editor_pic = ['chenchen.png', 'miaomiao.png', 'nana.png', 'xiaofang.png', 'xiaoyi.png', 'xiaozhi.png']
    editor_pic = ['chenchen.png', 'xiaozhi.png']
    center_group = {
        '3': '名片全能王3群-商务资源对接',
        '19': '名片全能王19群-商务资源对接',
        '20': '名片全能王20群-商务资源对接',
        # 'test1': '微信机器人开发',
    }

    def __init__(self, env='DEV', id='robot_id', duty='robot', enableCmdQR=False, qrCallback=False, hotReload=False, blockThread=False):
        self.env = env
        if id=='robot_id':
            self.id = 'robot_'+ str(int(time.time()))
            # self.id = 'robot_id'
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
        # enableCmdQR = 2 if 'Linux' in platform.platform() else False
        enableCmdQR = False
        super().__init__(env=env, duty='robot admin', enableCmdQR=enableCmdQR, blockThread=True)
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
        editor_robot = self.robot.search_friends(name=value['robot_name'])
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

