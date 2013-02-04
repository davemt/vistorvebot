import threading
import base as robotbase

## TODO: Should this live in globalconfig
COMMAND_INTERVAL = .1

def run_robot_command(robot_obj, line, request):
    """Parses the command from the web socket and runs it on our robot object"""
    command = line.rstrip().split(None)
    try:
        method = getattr(robot_obj, command[0])
    except AttributeError:
        request.ws_stream.send_message("ERROR: Unrecognized Command: %s" % command[0])
        return
    method(*command[1:])
    request.ws_stream.send_message("OK: %s with args: %s" %
                         (command[0], str(command[1:])))

class RobotControl(object):
    def __init__(self):
        self.timer = self._generate_timer()
        ## TODO: Attempt to autodetect usb port (ls /dev/tty*)
        self.robot = robotbase.Create('/dev/ttyUSB0')
        self.robot.SoftReset()
        self._ensure_control_mode()

    def _generate_timer(self):
        """Stop after ``COMMAND_INTERVAL`` seconds"""
        return threading.Timer(COMMAND_INTERVAL + .1, self.stop)

    def start_safety_timer(self):
        """Any time we run an action command, we start a timer that will
        stop the robot if it is not canceled after some amount of time"""
        self.timer.cancel()
        self.timer = self._generate_timer()
        self.timer.start()

    def _ensure_control_mode(self):
        """Make sure the robot is in control mode"""
        self.robot.Control()

    def _prepare_action_method(self):
        """This is a method to be run before every action method. In a perfect
        world it would be a decorator on those methods, but that is tough
        inside this class"""
        #self._ensure_control_mode()
        self.start_safety_timer()

    def forward(self, velocity=robotbase.VELOCITY_FAST):
        self._prepare_action_method()
        self.robot.DriveStraight(velocity)

    def forward_right(self, velocity=robotbase.VELOCITY_FAST, radius=robotbase.RADIUS_RIGHT):
        self._prepare_action_method()
        self.robot.Drive(velocity, radius)

    def forward_left(self, velocity=robotbase.VELOCITY_FAST, radius=robotbase.RADIUS_LEFT):
        self._prepare_action_method()
        self.robot.Drive(velocity, radius)

    def backward(self, velocity=robotbase.VELOCITY_FAST):
        self._prepare_action_method()
        self.robot.DriveStraight(-velocity)

    def backward_right(self, velocity=robotbase.VELOCITY_FAST, radius=robotbase.RADIUS_RIGHT):
        self._prepare_action_method()
        self.robot.Drive(-velocity, radius)

    def backward_left(self, velocity=robotbase.VELOCITY_FAST, radius=robotbase.RADIUS_LEFT):
        self._prepare_action_method()
        self.robot.Drive(-velocity, radius)

    def left_in_place(self, velocity=robotbase.VELOCITY_SLOW):
        self._prepare_action_method()
        self.robot.TurnInPlace(velocity, 'ccw')

    def right_in_place(self, velocity=robotbase.VELOCITY_SLOW):
        self._prepare_action_method()
        self.robot.TurnInPlace(velocity, 'cw')

    def stop(self):
        self._ensure_control_mode()
        self.robot.Stop()

    def print_args(self, *args):
        """A test function to make sure the web socket is working"""
        print args
