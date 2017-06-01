import time
from bson import ObjectId
import json
import pymongo
import redis
from celery import Celery, platforms
import sys
sys.path.append('..')
import conf.config as config
from crontab import const


app = Celery('tasks')
app.config_from_object('task_config')
platforms.C_FORCE_ROOT = True

def connect_redis():
    connection = redis.Redis(
        host=config.REDIS[const.ENV]['host'],
        port=int(config.REDIS[const.ENV]['port']),
        db=int(config.REDIS[const.ENV]['db']),
        password=config.REDIS[const.ENV]['password']
    )
    return connection

def connect_mongo():
    conn = pymongo.MongoClient(config.MONGO[const.ENV]['host'], int(config.MONGO[const.ENV]['port']))
    db = eval("conn." + config.MONGO[const.ENV]['db'])
    ret = db.authenticate(config.MONGO[const.ENV]['user'], config.MONGO[const.ENV]['password'],
                          config.MONGO[const.ENV]['db'])
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
                db.task.find_one_and_update({'_id':ObjectId(record['_id'])}, {'$set':{'status':2}})
        start += step
    client.close()
    return True