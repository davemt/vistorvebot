WEBAPP_HOST = "http://localhost:8080"

INITIALIZE_SESSION_METHOD = "/new_session/"
ACTIVATE_SESSION_METHOD = "/begin_control/"

HANGOUT_JOIN_URL = "https://hangoutsapi.talkgadget.google.com/hangouts/_?gid=478475668397"
HEARTBEAT_INTERVAL = 10 # Seconds

WEBAPP_HEARTBEAT_URL = "%s/robotarmy/robot-heartbeat/" # Expects ip and active (1 or 0)
WEBAPP_SESSION_ENDED_URL = "%s/robotarmy/robot-session-ended/" # Expects ip in GET

ROBOT_JOIN_TIMEOUT = 30 # Length of time to wait for the robot to join
