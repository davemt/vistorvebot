import os
import errno
import shutil

import config

SESSION_ID_FILE = os.path.join(config.SESSION_DIR, 'sid')

class SessionConflict(Exception):
    pass

def generate_session_id():
    import sha, time
    return sha.new(str(time.time())).hexdigest()

def init_session():
    # attempt to create session directory (acts as lock!)
    try:
        os.mkdir(config.SESSION_DIR)
    except OSError as e:
        if e.errno == errno.EISDIR or e.errno == errno.EEXIST:
            raise SessionConflict("A session is already in progress.")
        raise
    # generate and store session id
    session_file = open(SESSION_ID_FILE, 'w')
    sid = generate_session_id()
    session_file.write(sid)
    session_file.close()
    return sid

def verify_session(sid):
    if not os.path.isdir(config.SESSION_DIR):
        # no session exists
        return False
    session_file = open(SESSION_ID_FILE)
    try:
        stored_sid = session_file.readlines()[0]
        assert sid == stored_sid
        return True
    except (IndexError, AssertionError):
        return False

def close_session(sid):
    # The following race condition is possible:
    #  1) We attempt to close session
    #  2) Session id matches and we're granted permission to close
    #  3) Another verified party attempts to close session
    #  4) Session id matches and they're granted permission to close
    #  5) Their delete of session directory happens first
    #  6) Another session is opened, which we are not allowed to close
    #  7) We still have permission, so we then delete the wrong session
    #     directory!
    if not verify_session(sid):
        raise SessionConflict("Session id did not match current session.")
    # close the session with an atomic rename, then clean up
    os.rename(config.SESSION_DIR, config.SESSION_DIR + sid)
    shutil.rmtree(config.SESSION_DIR + sid)
