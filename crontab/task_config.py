from __future__ import absolute_import
from celery.schedules import crontab
from datetime import timedelta
from crontab import const
import sys
sys.path.append('..')
import conf.config as config

BROKER_URL = 'redis://:{}@{}:{}/{}'.format(
    config.REDIS[const.ENV]['password'],
    config.REDIS[const.ENV]['host'],
    config.REDIS[const.ENV]['port'],
    config.REDIS[const.ENV]['db'],
)

CELERYBEAT_SCHEDULE = {
    'group-invite-every-minute': {
        'task': 'tasks.group_invite',
        'schedule': crontab(hour=24),
        'args': (),
    },
    # 'add-every-5-seconds': {
    #     'task': 'tasks.add',
    #     'schedule': timedelta(seconds=5),
    #     'args': (16, 10),
    # },
}

CELERY_TIMEZONE = 'UTC'