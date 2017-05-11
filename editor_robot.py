import os
from random import choice
import itchat
from itchat.content import *


class EditorRobot(object):
    division_group_map = {
        '1023': '名片全能王 - 机械机电自动化交流群',
        '1024': '名片全能王 - 金融行业交流群',
        '1025': '名片全能王 - IT互联网行业交流群',
        '1026': '名片全能王 - 房产建筑行业交流群',
        '1027': '名片全能王 - 快消零售交流群',
        '1028': '名片全能王 - 广告媒体交流群',
        '1029': '名片全能王 - 教育行业交流群',
        '1030': '名片全能王 - 医疗行业交流群',
        '1031': '名片全能王 - 电子电器行业交流群',
        '1032': '名片全能王 - 交通运输物流交流群',
        '1033': '名片全能王 - 化工行业交流群',
        '1034': '名片全能王 - 冶炼五金交流群',
        '1035': '名片全能王 - 能源资源交流群',
    }
    # editor_pic = ['chenchen.png', 'miaomiao.png', 'nana.png', 'xiaofang.png', 'xiaoyi.png', 'xiaozhi.png']
    editor_pic = ['chenchen.png', 'xiaozhi.png']
    center_group = ['名片全能王3群-商务资源对接', '名片全能王19群-商务资源对接', '名片全能王20群-商务资源对接']

    def __init__(self, id, robot):
        self.id = id
        self.robot = robot


class FenqunRobot(EditorRobot):

    def __init__(self, id, robot):
        EditorRobot.__init__(self, id, robot)

        @robot.msg_register([TEXT])
        def auto_reply(msg):
            '''
            用户回复数字，发送分群链接；否则，自动回复文案
            :param msg:
            :return:
            '''
            auto_reply = '''这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的免费共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

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

            if msg['Text'] in FenqunRobot.division_group_map.keys():
                friend = robot.search_friends(userName=msg['FromUserName'])
                print('friend----------------------->', friend)
                chatrooms = robot.search_chatrooms(name=FenqunRobot.division_group_map.get(msg['Text']))
                print('chatrooms-------------------->', chatrooms)
                if friend and chatrooms:
                    robot.add_member_into_chatroom(chatrooms[0]['UserName'], [friend], useInvitation=True)
            else:
                robot.send(auto_reply, msg['FromUserName'])

        @robot.msg_register(FRIENDS)
        def add_friend(msg):
            '''
            自动加好友，并回复入群指示
            :param msg:
            :return:
            '''
            robot.add_friend(**msg['Text'])
            auto_reply = '''这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的免费共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

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
            robot.send(auto_reply, msg['RecommendInfo']['UserName'])

    def run(self, qr_callback):
        Dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'editor_data')
        self.robot.auto_login(hotReload=True, statusStorageDir=os.path.join(Dir, self.id+'.pkl'),
                              picDir=os.path.join(Dir, self.id+'.png'), qrCallback=qr_callback)
        self.robot.run(blockThread=False)


class ZongqunRobot(EditorRobot):
    def __init__(self, id, robot):
        EditorRobot.__init__(self, id, robot)

        @robot.msg_register([PICTURE])
        def add_group_reply(msg):
            '''
            收到用户截图，发送总群链接
            :param msg:
            :return:
            '''
            friend = robot.search_friends(userName=msg['FromUserName'])
            print('friend----------------------->', friend)
            chatrooms = robot.search_chatrooms(name=choice(EditorRobot.center_group))
            print('chatrooms-------------------->', chatrooms)
            if friend and chatrooms:
                robot.add_member_into_chatroom(chatrooms[0]['UserName'], [friend], useInvitation=True)

        @robot.msg_register(FRIENDS)
        def add_friend(msg):
            '''
            自动加好友，并回复自我介绍和入群指示
            :param msg:
            :return:
            '''
            robot.add_friend(**msg['Text'])
            auto_reply = '''您好，我是名片全能王社群的群小蜜，请仔细阅读下方文字哦：

【入群必读】
这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

【进群门槛】
本社群不收取任何会费，所有服务皆免费，为了壮大我们的社群，有一个小小的请求，希望您将以下海报分享到朋友圈并截图发给我，我才会拉你入群哦！非常感谢您的配合。 

【分享如下海报到朋友圈】'''
            robot.send(auto_reply, msg['RecommendInfo']['UserName'])
            data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'master_data')
            robot.send('@img@{}'.format(os.path.join(data_dir, choice(EditorRobot.editor_pic))), msg['RecommendInfo']['UserName'])

    def run(self, qr_callback):
        Dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'editor_data')
        self.robot.auto_login(hotReload=True, statusStorageDir=os.path.join(Dir, self.id + '.pkl'),
                              picDir=os.path.join(Dir, self.id + '.png'), qrCallback=qr_callback)
        self.robot.run(blockThread=False)