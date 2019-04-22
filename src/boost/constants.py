from collections import namedtuple

MotorControllerConstants = namedtuple('MotorControllerConstants', 'power_definitions ramp_up_time_from_zero_to_max_in_sec')

RuntimeParameters = namedtuple('RuntimeParameters', 'num_turn_sections num_speeds')
