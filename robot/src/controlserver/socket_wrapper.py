import os, sys
from mod_pywebsocket.standalone import _main as main

# We need to do this because the script itself reads our *_wsh.py file
# as a string and execs it, so we have to define the path outside
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    main()
