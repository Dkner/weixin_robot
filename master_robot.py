import os
import time
import itchat
import pymongo
import redis
from conf import config


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

