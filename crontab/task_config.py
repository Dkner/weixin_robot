from __future__ import absolute_import
from celery.schedules import crontab
from datetime import timedelta

BROKER_URL = 'redis://:111111@192.168.8.30:6379/1'

CELERYBEAT_SCHEDULE = {
    'group-invite-every-minute': {
        'task': 'tasks.group_invite',
        'schedule': crontab(minute='*'),
        'args': (),
    },
}

# CELERYBEAT_SCHEDULE = {
#     'add-every-2-seconds': {
#         'task': 'tasks.add',
#         'schedule': timedelta(seconds=2),
#         'args': (16, 10),
#     },
# }

CELERY_TIMEZONE = 'UTC'