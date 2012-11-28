import os

from bottle import route, run, request, abort

import config
from multiprocessing import Process
from session import init_session, verify_session, close_session, SessionConflict
from hangouts import start_hangout, stop_hangout, get_hangout_control_port

@route('/new_session/')
def new_session():
    """Acquire a new robot control session.  If successful, other parties are
    blocked from acquiring a session."""
    try:
        sid = init_session() 
    except SessionConflict, e:
        # TODO how do we skip the html generation that abort does?
        abort(409, "Unable to acquire control session id: %s" % str(e))
    return {'sid': sid}


@route('/begin_control/:sid/')
def begin_control(sid):
    """Begin the robot control session. Requires the GET parameter
    'hangout_url' to join the control hangout."""
    if not verify_session(sid):
        # TODO response code/text
        abort()

    url = request.params.get('hangout_url')
    if not url:
        # TODO response code/text
        abort()

    p = Process(target=start_hangout, name="selenium-hangout", args=[url])
    p.start()

    return {'message': "Control is starting; joining the hangout."}


@route('/end_session/:sid/')
def end_session(sid):
    """End a robot control session.  After session is ended, another party
    can then acquire a new session."""
    try:
        # TODO can we move this port stuff to hangouts.py?
        #  The issue was that close_session deletes the session directory,
        #  which clears out the port storage file.  But we don't want to
        #  stop the hangout before we validate sid & close session.
        port = get_hangout_control_port()
        close_session(sid)
        stop_hangout(port)
        return {'message': "Session ended successfully."}
    except SessionConflict, e:
        abort(409, "Unable to end control session: %s" % str(e))


if __name__ == '__main__':
    run(host=config.ADMINSERVER_HOST, port=config.ADMINSERVER_PORT)
