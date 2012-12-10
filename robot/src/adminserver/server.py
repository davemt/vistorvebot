import os

from bottle import route, run, request, abort

import config
from multiprocessing import Process
from session import Session, SessionConflict
from hangouts import start_hangout, stop_hangout

@route('/new_session/')
def new_session():
    """Acquire a new robot control session.  If successful, other parties are
    blocked from acquiring a session."""
    try:
        session = Session.initialize() 
    except SessionConflict, e:
        # TODO how do we skip the html generation that abort does?
        abort(409, str(e))
    return {'sid': session.sid}


@route('/begin_control/:sid/')
def begin_control(sid):
    """Begin the robot control session. Requires the GET parameter
    'hangout_url' to join the control hangout."""
    try:
        Session(sid)
    except SessionConflict, e:
        abort(409, str(e))

    url = request.params.get('hangout_url')
    if not url:
        abort(400, "Get parameter 'hangout_url' is required.")

    p = Process(target=start_hangout, name="selenium-hangout", args=[url, sid])
    p.start()

    return {'message': "Control is starting; joining the hangout."}


@route('/end_session/:sid/')
def end_session(sid):
    """End a robot control session.  After session is ended, another party
    can then acquire a new session."""
    try:
        # TODO can we move this port stuff to hangouts.py?
        #  The issue was that Session.close deletes the session directory,
        #  which clears out the port storage file.  But we don't want to
        #  stop the hangout before we validate sid & close session.
        session = Session(sid)
        port = session.get('hangout_control_port')
        session.close()
        stop_hangout(port)
        return {'message': "Session ended successfully."}
    except SessionConflict, e:
        abort(409, "Unable to end control session: %s" % str(e))


if __name__ == '__main__':
    run(host=config.ADMINSERVER_HOST, port=config.ADMINSERVER_PORT)
