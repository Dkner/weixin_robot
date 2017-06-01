from crontab import const
from configparser import ConfigParser
cfg = ConfigParser()
cfg.read('../../config/config.ini')
const.ENV = cfg.get('env', 'environment')