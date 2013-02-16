from bottle import route, run, request, abort

import config
from multiprocessing import Process
from session import Session, SessionConflict, SessionDoesNotExist
from hangouts import start_hangout, stop_hangout
import heartbeats

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
    #
    # TODO this can be called repeatedly and opens up multiple selenium hangouts!
    #
    try:
        Session(sid)
    except SessionConflict, e:
        abort(409, str(e))
    except SessionDoesNotExist, e:
        abort(404, "Requested session does not exist.")

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
        heartbeats.send_session_ended()
        return {'message': "Session ended successfully."}
    except SessionConflict, e:
        abort(409, "Unable to end control session: %s" % str(e))
    except SessionDoesNotExist:
        abort(404, "Requested session does not exist.")


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage="usage: python %prog [options]")
    parser.add_option('-H', '--no-heartbeats', dest='heartbeats',
                      action="store_true", default=True,
                      help="Do not start the heartbeat process to send "
                           "periodic heartbeats to the webapp.")
    parser.add_option('-c', '--cleanup-session', dest='cleanup_session',
                      action="store_true", default=False,
                      help="Delete any stored session state when server "
                           "starts up.")
    options, args = parser.parse_args()

    if options.heartbeats:
        print("Starting heartbeat sender process, logging to %s...\n" %
              config.HEARTBEATS_LOGFILE)
        # start the periodic heartbeat sender
        heartbeats.start()

    if options.cleanup_session:
        # delete any stored session state
        print("Deleting existing session state...")
        Session.full_cleanup()

    # start the admin server
    run(host=config.ADMINSERVER_HOST, port=config.ADMINSERVER_PORT)
