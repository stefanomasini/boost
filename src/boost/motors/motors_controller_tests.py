import unittest
from datetime import datetime, timedelta
from .motors_controller import MotorsController
from ..constants import MotorControllerConstants


class FakeClock(object):
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now

    def add(self, td):
        self._now = self._now + td


class MotorsControllerTestSuite(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock(datetime(2019, 4, 9, 22, 5, 0))  # 9 Apr 2019 - 22:05
        self.constants = MotorControllerConstants([0.2, 0.4, 0.6, 0.8, 1.0], 1.0)
        self.controller = MotorsController(self.clock, ['A', 'B'])
        self.motor_power = {}

    def set_motor_power(self, motor, power):
        self.motor_power[motor] = power

    def test_ramp_up_from_zero_to_max_and_to_minus_max(self):
        self.controller.set_target_speed('A', 5, self.constants)
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 0, 'B': 0})

        # Half way through
        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 0.5, 'B': 0})

        # At the end of the ramp-up
        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 1.0, 'B': 0})

        # After ramp up, power remains the same
        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 1.0, 'B': 0})

        # Now ramping all the way to opposite
        self.controller.set_target_speed('A', -5, self.constants)
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 1.0, 'B': 0})

        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 0.5, 'B': 0})

        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 0, 'B': 0})

        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': -0.5, 'B': 0})

        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': -1.0, 'B': 0})

        self.clock.add(timedelta(seconds=0.5))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': -1.0, 'B': 0})

    def test_ramping_separate_motors(self):
        self.controller.set_target_speed('A', 5, self.constants)
        self.controller.set_target_speed('B', -5, self.constants)
        self.clock.add(timedelta(seconds=1))
        self.controller.apply_motor_power(self)
        self.assertEqual(self.motor_power, {'A': 1.0, 'B': -1.0})
