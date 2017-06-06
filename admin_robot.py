import json
import os
import platform
import threading
from itchat.content import *
from master_robot import Robot
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