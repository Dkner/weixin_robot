import redis
import json
import config


def connect_redis():
    connection = redis.Redis(host=config.REDIS['DEV']['host'], port=int(config.REDIS['DEV']['port']),
                             db=int(config.REDIS['DEV']['db']),
                             password=config.REDIS['DEV']['password'])
    return connection

redis = connect_redis()
command = {
    'key': 'group_invite',
    'value': {
        'robot_name': '亮',
        'user_name': '名片全能王-管理员_1495186431'
        # 'user_name': ''
    }
}
ret = redis.rpush('weixin_robot_admin_command',json.dumps(command))
print(ret)