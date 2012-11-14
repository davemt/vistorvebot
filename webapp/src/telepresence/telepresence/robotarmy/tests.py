import time
from django.test.client import Client
from django.utils import unittest
from django.db import transaction

from telepresence.robotarmy.models import Robot

@transaction.commit_on_success
def delete_all_robots():
    # TODO: This is stupid -- need a custom runner, or commit_unless_managed
    Robot.objects.all().delete()

class RobotHeartBeatTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_new_robot_from_heartbeat(self):
        delete_all_robots()
        response = self.client.get('/robotarmy/robot-heartbeat/')
        key = response.content
        created_robot = Robot.objects.all().get()
        self.assertEqual(created_robot.secret_key, key)


    def test_heartbeat_on_existing_robot_without_key(self):
        delete_all_robots()
        # Create a robot
        self.client.get('/robotarmy/robot-heartbeat/')
        # Try to get to it
        response1 = self.client.get('/robotarmy/robot-heartbeat/')
        # Now we make another heartbeat without passing the code
        response2 = self.client.get('/robotarmy/robot-heartbeat/')
        self.assertEqual(response2.status_code, 401)

    def test_heartbeat_on_existing_robot_with_incorrect_key(self):
        delete_all_robots()
        # Create a robot
        self.client.get('/robotarmy/robot-heartbeat/')
        # Try to get to it
        response1 = self.client.get('/robotarmy/robot-heartbeat/')
        # Now we make another heartbeat with a bad code
        response2 = self.client.get('/robotarmy/robot-heartbeat/?key=123')
        self.assertEqual(response2.status_code, 401)

    def test_heartbeat_on_existing_active_robot_updates_state_and_ts(self):
        delete_all_robots()
        response1 = self.client.get('/robotarmy/robot-heartbeat/')
        key = response1.content

        robot = Robot.objects.all().get()
        orig_ts = robot.last_heartbeat
        time.sleep(1)

        response2 = self.client.get('/robotarmy/robot-heartbeat/?active=1&key=%s' % key)

        robot = Robot.objects.all().get()
        new_ts = robot.last_heartbeat

        self.assertGreater(new_ts, orig_ts)
        self.assertEqual(robot.state, Robot.STATE_ACTIVE)

    def test_heartbeat_on_existing_inactive_robot_updates_state_and_ts(self):
        delete_all_robots()
        response1 = self.client.get('/robotarmy/robot-heartbeat/')
        key = response1.content

        robot = Robot.objects.all().get()
        orig_ts = robot.last_heartbeat
        time.sleep(1)

        response2 = self.client.get('/robotarmy/robot-heartbeat/?key=%s' % key)

        robot = Robot.objects.all().get()
        new_ts = robot.last_heartbeat

        self.assertGreater(new_ts, orig_ts)
        self.assertEqual(robot.state, Robot.STATE_READY)


class RobotStateTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_state_stays_the_same_if_interval_is_large(self):
        delete_all_robots()
        self.client.get('/robotarmy/robot-heartbeat/')
        robot = Robot.objects.all().get()
        orig_state = robot.state
        new_state = robot.refresh_state(100)
        self.assertEqual(orig_state, new_state)
        # Make sure that robot state is the same as new_state
        robot = Robot.objects.all().get()
        self.assertEqual(robot.state, new_state)

    def test_state_robot_dies_if_interval_is_small(self):
        delete_all_robots()
        self.client.get('/robotarmy/robot-heartbeat/')
        robot = Robot.objects.all().get()
        new_state = robot.refresh_state(0) # Interval of 0
        self.assertEqual(Robot.STATE_DEAD, new_state)
        # Make sure that robot state is the same as new_state
        robot = Robot.objects.all().get()
        self.assertEqual(robot.state, new_state)


class RobotEndSessionTestCase(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_end_robot_session(self):
        delete_all_robots()
        # Create a robot
        response1 = self.client.get('/robotarmy/robot-heartbeat/')
        key = response1.content

        # Activate it
        self.client.get('/robotarmy/robot-heartbeat/?active=1&key=%s' % key)
        robot = Robot.objects.all().get()
        # End it
        self.client.get('/robotarmy/robot-session-ended/?key=%s' % key)
        robot = Robot.objects.all().get()
        self.assertEqual(robot.state, Robot.STATE_READY)

    def test_end_robot_session_not_authorized(self):
        delete_all_robots()
        # Create a robot
        response1 = self.client.get('/robotarmy/robot-heartbeat/')

        # Try to end it
        response2 = self.client.get('/robotarmy/robot-session-ended/')
        self.assertEqual(response2.status_code, 401)
