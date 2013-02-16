import simplejson
import urllib2
import httplib
from telepresence import globalconfig

from django.db import models, connection
from django.contrib.auth.hashers import check_password, make_password

class RobotManager(models.Manager):
    def update_heartbeat_and_state(self, ip, state):
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE robotarmy_robot
            SET last_heartbeat = DATETIME('now'), state = %s
            WHERE ip = %s;
            """,  [state, ip]
        )
        cursor.execute("select last_heartbeat from robotarmy_robot limit 1")


class Robot(models.Model):
    STATE_READY, STATE_DEAD, STATE_ACTIVE, STATE_SLEEPING = (
        'ready', 'dead', 'active', 'sleeping'
    )
    STATE_CHOICES = (
        (STATE_READY, "Ready to rock"),
        (STATE_DEAD, "He's dead, Jim"),
        (STATE_ACTIVE, "Do not disturb!"),
        # (STATE_SLEEPING, "zzzzzzzZZzzz"),
    )

    DEFAULT_PORT = 80

    state = models.CharField(max_length=10, default=STATE_READY, choices=STATE_CHOICES)
    last_state_change = models.DateTimeField(auto_now=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    secret_key = models.CharField(max_length=128)
    ip = models.IPAddressField(unique=True)
    port = models.IntegerField(default=DEFAULT_PORT)

    objects = RobotManager()

    def __unicode__(self):
        return self.ip + ":" + str(self.port)

    def set_secret_key(self, raw_key):
        self.secret_key = make_password(raw_key)

    def check_secret_key(self, raw_key):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_key):
            self.set_secret_key(raw_key)
            self.save()
        return check_password(raw_key, self.secret_key, setter)

    def refresh_state(self, interval=globalconfig.HEARTBEAT_INTERVAL):
        """Gets (and sets) the state based on the timestamp of the last heartbeat
        and the HEARTBEAT_INTERVAL, and returns the resulting state."""
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT STRFTIME('%%s', DATETIME('now')) - STRFTIME('%%s', last_heartbeat)
            FROM robotarmy_robot
            WHERE id = %s
            """, [self.pk]
        )
        time_since_hb = cursor.fetchone()[0]
        if time_since_hb >= interval:
            # Update the robot state with a 'lock'
            robot_updated = Robot.objects.filter(
                pk=self.pk, state=self.state
                ).update(state=Robot.STATE_DEAD)
            if robot_updated == 0: # We lost the lock, so try again
                self.state = Robot.objects.get(pk=self.pk).get_state()
            else:
                self.state = Robot.STATE_DEAD

        return self.state

    @property
    def url_root(self):
        return "https://" + self.ip + ":" + str(self.port)

    @property
    def initialize_session_url(self):
        return self.url_root + globalconfig.INITIALIZE_SESSION_METHOD

    def get_activate_session_url(self, session_id):
        url = self.url_root + globalconfig.ACTIVATE_SESSION_METHOD + "%s/"
        return url % session_id

    @property
    def websocket_control_url(self):
        url = "wss://" + self.ip + ":9435/control"
        return url

    def initialize_session(self, request):
        """Makes a request to the robot for a new session id and returns the
        hangout URL with the session_id and the robout URL passed as params"""
        try:
            sock = urllib2.urlopen(self.initialize_session_url)
        except urllib2.HTTPError:
            return {"error": True, "message": "The robot didn't like your request"}
        except urllib2.URLError:
            return {"error": True, "message": "The robot might be down"}
        except httplib.HTTPException:
            return {"error": True, "message": "Something strange is happening down robot way"}

        try:
            data = simplejson.loads(sock.read())
        except simplejson.JSONDecodeError:
            return {"error": True, "message": "The robot is speaking nonsense"}
        sid = data['sid']

        ## TODO: The status is not getting updated when we start up!
        self.refresh_state()
        # Update the robot state with a 'lock'
        robot_updated = Robot.objects.filter(
            pk=self.pk, state=Robot.STATE_READY
            ).update(state=Robot.STATE_ACTIVE)
        if robot_updated == 0: # TODO: Do we need to delete the session here?
            return {"error": True, "message": "Somebody else got to me first"}

        return {
            "error": False,
            "activate_session_url": self.get_activate_session_url(sid),
            "websocket_control_url": self.websocket_control_url,
            "hangout_javascript_url": globalconfig.WEBAPP_HOST + globalconfig.HANGOUT_JAVASCRIPT_URL,
            "hangout_function": "hangout",
            "sid": sid,
         }
