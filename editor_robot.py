import os
import itchat
from itchat.content import *


class EditorRobot(object):

    def __init__(self, id, robot):
        self.id = id
        self.robot = robot

        @robot.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
        def auto_reply(msg):
            auto_reply = '''【进群前，请仔细阅读名片全能王社群 - 群规】
1. 本群为实名商务社群，入群后先修改自己的群昵称：地域+行业+职位+姓名。
2. 请将自己的电子名片发至群内，方便大家互相收藏，更方便快捷的完成合作需求对接。
3. 请勿大量私加群友进行推销等骚扰行为，一经举报则将清除社群，并列出名片全能王社群黑名单。
4. 严禁转发信息早报，广告，娱乐短视频，投票等与群主题无关的信息，发现立即清除出群。
5. 禁止在社群内发布其他社群的二维码（包含文字，二维码等）'''
            if 'cc' in msg['Text']:
                robot.send(auto_reply, msg['FromUserName'])

        @robot.msg_register([PICTURE])
        def add_group_reply(msg):
            friend = robot.search_friends(userName=msg['FromUserName'])
            print('friend----------------------->',friend)
            chatrooms = robot.search_chatrooms(name='CC微信机器人开发')
            print('chatrooms-------------------->',chatrooms)
            robot.add_member_into_chatroom(chatrooms[0]['UserName'], [friend], useInvitation=True)

        @robot.msg_register(FRIENDS)
        def add_friend(msg):
            robot.add_friend(**msg['Text'])  # 该操作会自动将新好友的消息录入，不需要重载通讯录
            opening_remarks = '''您好，我是名片全能王社群的群小蜜，请仔细阅读下方文字哦：
【入群必读】
这是由名片全能王筹建的商务合作社群，是人脉共享，资源对接的共享平台，名片全能王app有2亿优质商务用户，目前社群人数30,000+，群数量100+。

【进群门槛】
因为名额有限，所以会有相应的限制。麻烦您将下图分享至朋友圈，并截图发回给我，审核通过后，会将您拉进群(注意:请勿分组或秒删)

【入群后福利】
1、免会费进入【名片全能王】社群，并且第一时间拿到精准客户需求。
2、将您的商务合作需求群发至100+个商务群，免费推广。
3、参与【名片全能王】专属活动及专属职场技能培训。

【分享如下海报到朋友圈】'''
            robot.send(opening_remarks, msg['RecommendInfo']['UserName'])
            data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'master_data')
            robot.send('@img@{}'.format(os.path.join(data_dir, 'opening_pic.png')), msg['RecommendInfo']['UserName'])

    def run(self, qrCallBack):
        print('new editor {} login...'.format(self.id))
        Dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'editor_data')
        self.robot.auto_login(hotReload=True, statusStorageDir=os.path.join(Dir, self.id+'.pkl'), picDir=os.path.join(Dir, self.id+'.png'), qrCallback=qrCallBack)
        self.robot.run(blockThread=False)