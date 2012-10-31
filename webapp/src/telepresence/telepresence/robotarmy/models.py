import simplejson
import urllib2
import httplib
from telepresence import globalconfig

from django.db import models, connection

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

    state = models.CharField(max_length=10, default=STATE_READY, choices=STATE_CHOICES)
    last_state_change = models.DateTimeField(auto_now=True)
    last_heartbeat = models.DateTimeField(null=True, blank=True)
    ip = models.IPAddressField(unique=True)
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name

    def refresh_state(self):
        """Gets (and sets) the state based on the timestamp of the last heartbeat
        and the HEARTBEAT_INTERVAL, and returns the resulting state."""
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT TIME_TO_SEC(TIMEDIFF(NOW(), last_heartbeat))
            FROM robotarmy_robot
            WHERE id = %s
            """, [self.pk]
        )
        time_since_hb = cursor.fetchone()[0]

        if time_since_hb > globalconfig.HEARBEAT_INTERVAL:
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
    def initialize_session_url(self):
        return "http://" + self.ip + globalconfig.INITIALIZE_SESSION_METHOD

    def get_activate_session_url(self, session_id):
        url = "http://" + self.ip + globalconfig.ACTIVATE_SESSION_METHOD + "%s"
        return url % session_id

    def initialize_session(self):
        """Makes a request to the robot for a new session id and returns the
        hangout URL with the session_id and the robout URL passed as params"""
        try:
            sock = urllib2.urlopen(self.initialize_session_url)
        except urllib2.HTTPError:
            return {"error":True, "message": "The robot didn't like your request"}
        except urllib2.URLError:
            return {"error":True, "message": "The robot might be down"}
        except httplib.HTTPException:
            return {"error":True, "message": "Something strange is happening down robot way"}

        try:
            data = simplejson.loads(sock.read())
        except simplejson.JSONDecodeError:
            return {"error":True, "message": "The robot is speaking nonsense"}
        sid = data['sid']

        # Update the robot state with a 'lock'
        robot_updated = Robot.objects.filter(
            pk=self.pk, state=Robot.STATE_READY
            ).update(state=Robot.STATE_ACTIVE)
        if robot_updated == 0:
            return {"error":True, "message": "Somebody else got to me first"}

        return {"error":False, "activate_session_url": self.get_activate_session_url(sid)}
