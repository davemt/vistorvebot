from django.db import models

class Robot(models.Model):
    STATE_READY, STATE_DEAD, STATE_ACTIVE, STATE_SLEEPING = (
        'ready', 'dead', 'active', 'sleeping'
    )
    STATE_CHOICES = (
        (STATE_READY, "Ready to rock"),
        (STATE_DEAD, "He's dead, Jim"),
        (STATE_ACTIVE, "Do not disturb!"),
        (STATE_SLEEPING, "zzzzzzzZZzzz"),
    )

    state = models.CharField(max_length=10, default=STATE_READY, choices=STATE_CHOICES)
    last_state_change = models.DateTimeField(auto_now=True)
    ip = models.IPAddressField()
    name = models.CharField(max_length=25)

    def __unicode__(self):
        return self.name

    def initialize_session(self):
        """Makes a request to the robot for a new session id and returns the
        hangout URL with the session_id and the robout URL passed as params"""
        
        # Returns a dict with Error: some error
        # OR
        # Returns a dict with a full activate_control_session url
        # like http://127.0.0.1:8080/activate_control_session?session_id=123
        # Returns error true/false
