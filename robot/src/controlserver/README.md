Control Server
==============

Currently we'll use pywebsocket to handle the requests coming from the google
app (control client). I downloaded the source to ~/src/pywebsocket-0.7.6, so
for me I start up the server from this directory as:

python ~/src/pywebsocket-0.7.6/src/mod_pywebsocket/standalone.py -p 9435 -w . --log_level debug

We could also possibly use tornado.websocket
