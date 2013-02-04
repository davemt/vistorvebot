Control Server
==============

Currently we'll use pywebsocket to handle the requests coming from the google
app (control client). First you will need to download the source and
run ``setup.py`` build and then ``sudo setup.py install`` python. After you've
done that, you can start the socket with::

  python socket_wrapper.py -p 9435 -w . --log_level debug

Couldn't we just run the following without the wrapper?::

  python -m mod_pywebsocket.standalone -p 9435 -w . --log_level debug

Once you've started up the server, you can send messages to it by using the console:

http://localhost:9435/console.html

Click "connect" to start the connection and then send messages!

You have access to any of the control methods listed in `RobotControl` which
lives in `pyrobot/control.py`. Initially, these include forward, backward,
left_in_place, and right_in_place.
