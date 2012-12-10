import os
import errno
import shutil

import config

def generate_session_id():
    import sha, time
    return sha.new(str(time.time())).hexdigest()


class SessionKeyError(Exception):
    """Raised when an expected key is not found in the session storage."""


class SessionDoesNotExist(Exception):
    """Raised when a given session can not be found."""


class SessionConflict(Exception):
    pass


class Session(object):
    def __init__(self, directory, sid):
        # access existing session
        if not os.path.isdir(directory):
            raise SessionDoesNotExist("Session directory '%s' does not exist." % directory)
        self.directory = directory
        self.sid = sid
        if not self._verify_sid(sid):
            raise SessionConflict("Session id did not match current session.")

    def _verify_sid(self, sid):
        self.get('sid')
        try:
            stored_sid = self.get('sid')
            assert sid == stored_sid
            return True
        except (SessionKeyError, AssertionError):
            return False

    @classmethod
    def initialize(cls, directory=config.SESSION_DIR):
        """Initialize a new session."""
        # attempt to create session directory (acts as lock!)
        try:
            os.mkdir(directory)
        except OSError as e:
            if e.errno == errno.EISDIR or e.errno == errno.EEXIST:
                raise SessionConflict("A session is already in progress.")
        # generate and store session id
        sid = generate_session_id()
        try:
            f = open(os.path.join(directory, 'sid'), 'w')
            f.write(sid + '\n')
            f.close()
        except IOError:
            raise IOError("Failed to store session id.")
        return cls(sid)

    def set(self, key, value):
        """Set the value of a key in the session storage."""
        try:
            f = open(os.path.join(self.directory, key), 'w')
            f.write(value + '\n')
            f.close()
        except IOError:
            raise IOError("Failed to set value for key '%s' in filestore." % key)

    def get(self, key):
        """Get the value of a key in the session storage."""
        try:
            f = open(os.path.join(self.directory, key), 'r')
        except IOError:
            raise SessionKeyError("Key '%s' not found in session store." % str(key))
        try:
            value = f.readlines()[0].strip()
        except IOError:
            raise IOError("Failed to get value for session store key '%s'." % key)
        except IndexError:
            # empty file
            return None
        return value

    def close(self):
        # The following race condition is possible:
        #  1) We attempt to close session
        #  2) Session id matches and we're granted permission to close
        #  3) Another verified party attempts to close session
        #  4) Session id matches and they're granted permission to close
        #  5) Their delete of session directory happens first
        #  6) Another session is opened, which we are not allowed to close
        #  7) We still have permission, so we then delete the wrong session
        #     directory!

        # close the session with an atomic rename, then clean up
        os.rename(self.directory, self.directory + self.sid)
        shutil.rmtree(self.directory + self.sid)


