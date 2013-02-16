Other Section
=============

Add content here

Robot Admin Server
==================

Requirements
------------

 * Install 'chromium-browser' package via apt-get or equivalent
 * Install google voice and video plugin
 * pip install -r requirements.txt
 * Download ChromeDriver binary for selenium, https://code.google.com/p/chromedriver/
   and make sure directory with 'chromedriver' binary is in PATH
   (good place to put 'chromedriver': <python-virtual-environment>/bin)
 * Make sure the following environment variables are defined (a good place is
   to append exports to your <python-virtual-env>/bin/activate file):
    - VBOT_CONTROL_SERVER_SCRIPT: full path to the ``controlserver/socket_wrapper.py``

Running the Server
------------------

Use the following command::

    python server.py
