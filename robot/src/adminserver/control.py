import os
from subprocess import Popen
import shlex

import config

CONTROL_SERVER_PORT = 9435

def start_controlserver():
    script = config.CONTROL_SERVER_SCRIPT
    if not os.path.exists(script):
        raise IOError("Could not locate controlserver script at %s." % script)
    port = CONTROL_SERVER_PORT
    logfile = config.CONTROL_SERVER_LOG_FILE
    key = config.TLS_KEY_PATH
    cert = config.TLS_CERT_PATH
    cmd = 'python %s -p %s -w -t -k %s -c %s . --log_level debug -l %s' % (
        script, port, key, cert, logfile)
    p = Popen(shlex.split(cmd))
    f = open(config.CONTROL_SERVER_PID_FILE, 'w')
    f.write(str(p.pid) + '\n')
    f.close()


def stop_controlserver():
    import signal
    pidfile = config.CONTROL_SERVER_PID_FILE
    try:
        pid = int(open(pidfile, 'r').read())
    except IOError:
        raise IOError("Could not locate controlserver PID file at %s." % pidfile)
    #
    # TODO QUESTION: why can't we use regular interrupt here?
    #
    os.kill(pid, signal.SIGINT)
    os.remove(pidfile)

