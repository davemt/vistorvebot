vistorvebot
===========

A cyber presence wonder

Starting the webapp
-------------------

    source ~/virtualenvs/vistorveapp/bin/activate
    python ~/projects/vistorvebot/webapp/src/telepresence/manage.py runserver 0.0.00:8080


Starting the robot adminserver
------------------------------

    source ~/virtualenvs/vistorvebot/bin/activate
    rm -rf /tmp/robot_session && python ~/projects/vistorvebot/robot/src/adminserver/server.py --send-heartbeats

Starting the websocket server
-----------------------------

This won't need to be done once the adminserver starts the websocket server
automatically.

    source ~/virtualenvs/vistorvebot/bin/activate
    python ~/projects/vistorvebot/robot/src/controlserver/socket_wrapper.py -p 9435 -w . --log_level debug
