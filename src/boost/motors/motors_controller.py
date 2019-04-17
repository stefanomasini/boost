from datetime import timedelta


class MotorsController(object):
    def __init__(self, clock, motor_names, power_definitions, ramp_up_time_in_sec):
        self.clock = clock
        self.current_power = dict((motor_name, 0) for motor_name in motor_names)
        self.speed_to_power_map = dict((idx+1, power_value) for idx, power_value in enumerate(power_definitions))
        maximum_power_value = power_definitions[-1]
        self.power_ramp_up_per_sec = maximum_power_value / ramp_up_time_in_sec
        self.ramp_up = dict((motor_name, None) for motor_name in motor_names)

    def set_target_speed(self, motor_name, speed):
        assert motor_name in self.current_power, 'Invalid motor {0}'.format(motor_name)
        assert speed in self.speed_to_power_map or -speed in self.speed_to_power_map, 'Invalid speed {0}'.format(speed)
        target_ramp_up_power = self.speed_to_power_map[speed] if speed > 0 else -self.speed_to_power_map[-speed]
        ramp_up = RampUp.calculate(self.current_power[motor_name], target_ramp_up_power, self.clock.now(), self.power_ramp_up_per_sec)
        self.ramp_up[motor_name] = ramp_up

    def stop_motor_immediately(self, motor_name):
        assert motor_name in self.current_power, 'Invalid motor {0}'.format(motor_name)
        self.current_power[motor_name] = 0
        self.ramp_up[motor_name] = None

    def apply_motor_power(self, adapter):
        for motor_name, ramp_up in self.ramp_up.items():
            if ramp_up:
                power = ramp_up.calculate_power(self.clock.now())
                self.current_power[motor_name] = power
        for motor_name, power in self.current_power.items():
            adapter.set_motor_power(motor_name, power)


class RampUp(object):
    @classmethod
    def calculate(cls, start_power, target_power, start_time, power_ramp_up_per_sec):
        power_diff = abs(target_power - start_power)
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

