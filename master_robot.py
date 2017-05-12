import os
import platform
import itchat
from itchat.content import *
from editor_robot import FenqunRobot, ZongqunRobot

QR_MAX_TRIED_COUNT = 0
HELP = '''你好！我是机器人管理员。
回复“总群机器人”——获取总群机器人的身份二维码
回复“分群机器人”——获取分群机器人的身份二维码

注意事项：
1）获取二维码之后扫描登录即可成为相应机器人
2）获取二维码后不登录超过一定时间，二维码会失效，若失效请重新操作
3）每个二维码只能供一个机器人使用
4）在微信中退出网页版登录即可退出机器人模式'''


@itchat.msg_register([TEXT])
def text_reply(msg):
    global QR_MAX_TRIED_COUNT
    QR_MAX_TRIED_COUNT = 0

    def add_editor_qr_callback(uuid, status, qrcode):
        global QR_MAX_TRIED_COUNT
        if QR_MAX_TRIED_COUNT<2:
            pic_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'editor_data', msg['FromUserName'] + '.png')
            with open(pic_file, 'wb') as f:
                f.write(qrcode)
            itchat.send('Please scan the QR code to log in.', msg['FromUserName'])
            itchat.send('@img@{}'.format(pic_file), msg['FromUserName'])
        elif QR_MAX_TRIED_COUNT>5 or str(status)=='408':
            itchat.send('Scan timeout, Please request again', msg['FromUserName'])
            exit(0)
        QR_MAX_TRIED_COUNT += 1

    if '总群机器人' in msg['Text']:
        editor = ZongqunRobot(id=msg['FromUserName'], robot=itchat.new_instance())
        editor.run(add_editor_qr_callback)
        itchat.send('login in as central robot success', msg['FromUserName'])
    elif '分群机器人' in msg['Text']:
        editor = FenqunRobot(id=msg['FromUserName'], robot=itchat.new_instance())
        editor.run(add_editor_qr_callback)
        itchat.send('login in as partial robot success', msg['FromUserName'])
    elif '使用说明' in msg['Text']:
        itchat.send(HELP, msg['FromUserName'])

master_data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'master_data')
if 'Linux' in platform.platform():
    enableCmdQR = 2
else:
    enableCmdQR = False
itchat.auto_login(hotReload=False, statusStorageDir=os.path.join(master_data_dir, 'master.pkl'), picDir=os.path.join(master_data_dir, 'QR.png'), enableCmdQR=enableCmdQR)
itchat.run(debug=True, blockThread=True)
