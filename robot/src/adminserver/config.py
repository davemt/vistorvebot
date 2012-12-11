ADMINSERVER_HOST = '0.0.0.0'
ADMINSERVER_PORT = '80'
DEBUG = True
# TODO of course... we should move this all out of temp
LOG_ROOT = '/tmp/robot_logs'
SESSION_DIR = '/tmp/robot_session'
WEBAPP_KEY_FILE = '/tmp/robot_webapp_key'
HEARTBEATS_PID_FILE = '/tmp/robot_heartbeats.pid'
HEARTBEATS_LOGFILE = '%s/heartbeats.log' % LOG_ROOT

import os
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)
