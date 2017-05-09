import os
import platform
import itchat
from itchat.content import *
from editor_robot import EditorRobot

qr_max_tried_count = 0

@itchat.msg_register([TEXT, MAP, CARD, NOTE, SHARING])
def text_reply(msg):
    print(msg)
    global qr_max_tried_count
    qr_max_tried_count = 0
    def editorQrCallBack(uuid, status, qrcode):
        global qr_max_tried_count
        if qr_max_tried_count<2:
            pic_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'editor_data', msg['FromUserName'] + '.png')
            with open(pic_file, 'wb') as f:
                f.write(qrcode)
            ret = itchat.send('Please scan the QR code to log in.', msg['FromUserName'])
            ret = itchat.send('@img@{}'.format(pic_file), msg['FromUserName'])
        elif qr_max_tried_count>5 or str(status)=='408':
            ret = itchat.send('Scan timeout, Please request again', msg['FromUserName'])
            exit(0)
        qr_max_tried_count += 1

    if 'master' in msg['Text']:
        editor = EditorRobot(id=msg['FromUserName'], robot=itchat.new_instance())
        editor.run(editorQrCallBack)

master_data_dir = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'master_data')
if 'Linux' in platform.platform():
    enableCmdQR = 2
else:
    enableCmdQR = False
itchat.auto_login(hotReload=True, statusStorageDir=os.path.join(master_data_dir, 'master.pkl'), picDir=os.path.join(master_data_dir, 'QR.png'), enableCmdQR=enableCmdQR)
itchat.run(blockThread=True)
