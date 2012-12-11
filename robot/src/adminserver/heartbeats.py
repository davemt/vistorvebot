import os
import sys
import urllib
import urllib2
import time
import json
import logging
from multiprocessing import Process

from globalconfig import WEBAPP_HOST, WEBAPP_HEARTBEAT_URL, \
    HEARTBEAT_INTERVAL, WEBAPP_SESSION_ENDED_URL
from config import WEBAPP_KEY_FILE, HEARTBEATS_PID_FILE, HEARTBEATS_LOGFILE

from session import Session

HEARTBEAT_URL = WEBAPP_HEARTBEAT_URL % WEBAPP_HOST
SESSION_ENDED_URL = WEBAPP_SESSION_ENDED_URL % WEBAPP_HOST

# TODO should send at normal interval, but webserver needs to be more lenient first
HEARTBEAT_INTERVAL = HEARTBEAT_INTERVAL/2

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename=HEARTBEATS_LOGFILE)


class HeartbeatAuthError(Exception):
    """Raised when there is an issue authenticating during communications with
    the webapp."""


def _get_webapp_key():
    try:
        f = open(WEBAPP_KEY_FILE, 'r')
        value = f.readlines()[0].strip()
        return value
    except IOError:
        return None


def _set_webapp_key(value):
    try:
        f = open(WEBAPP_KEY_FILE, 'w')
        f.write(value + '\n')
        f.close()
    except IOError:
        raise IOError("Failed to store webapp auth key.")


def send_heartbeat():
    """Send a heartbeat request to the webapp to notify it of the robot's
    status."""
    auth_key = _get_webapp_key()
    if auth_key:
        # webapp should know about this robot; send a status heartbeat
        active = Session.check_session_exists()

        # TODO here we would determine if our websocket is open, etc.
        #  and 'active' might become false

        active = 1 if active else 0
        params = urllib.urlencode({'key': auth_key, 'active': active})
        url = HEARTBEAT_URL + '?' + params
        try:
            response = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            if e.code == 403:
                raise HeartbeatAuthError("Auth key was not accepted by webserver.")
            else:
                raise
    else:
        # this robot was just discovered, and now should get an auth key
        response = urllib2.urlopen(HEARTBEAT_URL).read()
        _set_webapp_key(response.strip())


def send_session_ended():
    """Send a request to the webapp to notify it that the robot control session
    has ended."""
    auth_key = _get_webapp_key()
    if auth_key:
        params = urllib.urlencode({'key': auth_key})
        url = SESSION_ENDED_URL + '?' + params
        try:
            response = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            if e.code == 403:
                raise HeartbeatAuthError("Auth key was not accepted by webapp.")
            elif e.code == 400:
                response = e.read()
            else:
                raise
        data = json.loads(response)
        if data['error']:
            raise Exception("An error occurred while telling the webapp that "
                            "session has ended: %s" % data['message'])
    else:
        raise HeartbeatAuthError("Missing webapp auth key file.")


def send_periodic_heartbeats(interval):
    while 1:
        try:
            send_heartbeat()
        except HeartbeatAuthError, e:
            logging.error(str(e))
        except Exception, e:
            logging.error(str(e))
            logging.error("Stopping heartbeat sender due to previous errors.")
            sys.exit(1)
        time.sleep(interval)


def start():
    p = Process(target=send_periodic_heartbeats, args=[HEARTBEAT_INTERVAL])
    p.start()
    f = open(HEARTBEATS_PID_FILE, 'w')
    f.write(str(p.pid) + '\n')
    f.close()


def stop():
    import signal
    try:
        pid = int(open(HEARTBEATS_PID_FILE, 'r').read())
    except IOError:
        raise IOError("Could not locate PID file at %s." % HEARTBEATS_PID_FILE)
    os.kill(pid, signal.SIGKILL)
    os.remove(HEARTBEATS_PID_FILE)


if __name__ == '__main__':
    usage = "usage: python heartbeats.py (start|stop)\n"
    try:
        cmd = sys.argv[1]
    except IndexError:
        sys.stderr.write(usage)
        sys.exit(1)

    if cmd == 'start':
        start()
    elif cmd == 'stop':
        stop()
    elif cmd == 'test':
        send_heartbeat()
    else:
        sys.stderr.write(usage)
        sys.exit(1)

