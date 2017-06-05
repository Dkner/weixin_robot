import pymongo

from conf import config

def connect_mongo():
    env = 'DEV'
    conn = pymongo.MongoClient(config.MONGO[env]['host'], int(config.MONGO[env]['port']))
    db = eval("conn." + config.MONGO[env]['db'])
    ret = db.authenticate(config.MONGO[env]['user'], config.MONGO[env]['password'],
                          config.MONGO[env]['db'])
    if not ret:
        return conn, False
    return conn, db

client, db = connect_mongo()
task_info = {
    'key': 'group_invite',
    'value': {
        'robot_name': '名片全能王-小助手-苗苗',
        'user_name': '亮_1496304663',
    },
    'trigger_time': 1496229713,
    'status': 1
}
db.task.insert(task_info)