from datetime import timedelta


# NOTE:
#  - positive speed = Counter-Clockwise (CCW) rotation
#  - negative speed = Clockwise (CW) rotation


class MotorsController(object):
    def __init__(self, clock, motor_names):
        self.clock = clock
        self.current_power = dict((motor_name, 0) for motor_name in motor_names)
        self.ramp_up = dict((motor_name, None) for motor_name in motor_names)

    def set_target_speed(self, motor_name, speed, constants):
        assert motor_name in self.current_power, 'Invalid motor {0}'.format(motor_name)
        self.ramp_up[motor_name] = _get_ramp_up(constants, self.current_power[motor_name], speed, self.clock.now())

    def stop_motor_immediately(self, motor_name):
        assert motor_name in self.current_power, 'Invalid motor {0}'.format(motor_name)
        self.current_power[motor_name] = 0
        self.ramp_up[motor_name] = None

    # To be called periodically to drive the motors adapter
    def apply_motor_power(self, adapter):
        for motor_name, ramp_up in self.ramp_up.items():
            if ramp_up:
                power = ramp_up.calculate_power(self.clock.now())
                self.current_power[motor_name] = power
        for motor_name, power in self.current_power.items():
            adapter.set_motor_power(motor_name, power)


def _get_power_from_speed(constants, speed):
    if speed == 0:
        return 0.0
    speed_to_power_map = dict((idx+1, power_value) for idx, power_value in enumerate(constants.power_definitions))
    assert speed in speed_to_power_map or -speed in speed_to_power_map, 'Invalid speed {0}'.format(speed)
    return speed_to_power_map[speed] if speed > 0 else -speed_to_power_map[-speed]


def _get_ramp_up(constants, current_power, speed, now):
    maximum_power_value = constants.power_definitions[-1]
    power_ramp_up_per_sec = maximum_power_value / constants.ramp_up_time_from_zero_to_max_in_sec
    target_ramp_up_power = _get_power_from_speed(constants, speed)
    return RampUp.calculate(current_power, target_ramp_up_power, now, power_ramp_up_per_sec)


class RampUp(object):
    @classmethod
    def calculate(cls, start_power, target_power, start_time, power_ramp_up_per_sec):
        power_diff = abs(target_power - start_power)
        if power_diff == 0:
            return None
        ramp_up_time_in_sec = power_diff / power_ramp_up_per_sec
        target_time = start_time + timedelta(seconds=ramp_up_time_in_sec)
        return cls(start_power, target_power, start_time, target_time)

    def __init__(self, start_power, target_power, start_time, target_time):
        self.start_power = start_power
        self.target_power = target_power
        self.start_time = start_time
        self.target_time = target_time
        self.power_ramp_up_per_sec = (target_power - start_power) / (target_time - start_time).total_seconds()

    def calculate_power(self, now):
        if now > self.target_time:
            return self.target_power
        elapsed_time_in_sec = (now - self.start_time).total_seconds()
        return self.start_power + self.power_ramp_up_per_sec * elapsed_time_in_sec

