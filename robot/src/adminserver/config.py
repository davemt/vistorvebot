import os

ADMINSERVER_HOST = '0.0.0.0'
ADMINSERVER_PORT = '8081'
DEBUG = True
# TODO different placement of these files
VBOT_HOME = '/tmp/vbot'
LOG_ROOT = '%s/log' % VBOT_HOME
SESSION_DIR = '%s/active_session' % VBOT_HOME
WEBAPP_KEY_FILE = '%s/webapp_key' % VBOT_HOME
HEARTBEATS_PID_FILE = '%s/heartbeats.pid' % VBOT_HOME
HEARTBEATS_LOGFILE = '%s/heartbeats.log' % LOG_ROOT
CONTROL_SERVER_SCRIPT = os.environ['VBOT_CONTROL_SERVER_SCRIPT']
CONTROL_SERVER_LOG_FILE = '%s/controlserver.log' % LOG_ROOT
CONTROL_SERVER_PID_FILE = '%s/controlserver.pid' % VBOT_HOME

# TODO: Put these someplace that makes sense
TLS_KEY_PATH = '../controlserver/server.key'
TLS_CERT_PATH = '../controlserver/server.crt'

if not os.path.exists(VBOT_HOME):
    os.makedirs(VBOT_HOME)
if not os.path.exists(LOG_ROOT):
    os.makedirs(LOG_ROOT)
