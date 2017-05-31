import time
from bson import ObjectId
import json
import pymongo
import redis
from celery import Celery, platforms

import sys
sys.path.append('..')
import conf.config as config

app = Celery('tasks')
app.config_from_object('task_config')
platforms.C_FORCE_ROOT = True


def connect_redis():
    env = 'DEV'
    connection = redis.Redis(host=config.REDIS[env]['host'], port=int(config.REDIS[env]['port']), db=int(
        config.REDIS[env]['db']),
                             password=config.REDIS[env]['password'])
    return connection

def connect_mongo():
    env = 'DEV'
    conn = pymongo.MongoClient(config.MONGO[env]['host'], int(config.MONGO[env]['port']))
    db = eval("conn." + config.MONGO[env]['db'])
    ret = db.authenticate(config.MONGO[env]['user'], config.MONGO[env]['password'],
                          config.MONGO[env]['db'])
    if not ret:
        return conn, False
    return conn, db

@app.task
def add(x,y):
    return x + y

@app.task
def group_invite():
    client, db = connect_mongo()
    if not client or not db:
        print('connect mongo failed')
        return False
    redis = connect_redis()
    if not redis:
        print('connect redis failed')
        return False
    count = db.task.count({'status':1})
    start, step = 0, 10
    while start < count:
        this_loop_records = db.task.find({'status':1}).limit(step).skip(start)
        for record in this_loop_records:
            if record.get('key') and record.get('trigger_time')>0 and record.get('trigger_time') < int(time.time()):
                print(record)
                record['_id'] = str(record['_id'])
                redis.rpush('weixin_robot_admin_command', json.dumps(record))
                db.task.find_and_modify({'_id':ObjectId(str(record['_id']))}, {'status':2})
        start += step
    client.close()