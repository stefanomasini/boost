from collections import namedtuple
from datetime import timedelta
from ..gray_code import generate_gray_codes


WheelPosition = namedtuple('WheelPosition', 'position angle code')


class ShaftEncoders(object):
    def __init__(self, sensors_adapter, devices, clock, stasis_timeout, max_speed, log_error_message):
        self.sensors_adapter = sensors_adapter
        self.devices = devices
        self.clock = clock
        self.stasis_timeout = timedelta(seconds=stasis_timeout)
        self.max_speed = max_speed  # Degrees per second
        self.log_error_message = log_error_message

        self._on_device_angle_changed = None
        self.current_positions = None
        self.last_position_ts = {}

        # Initialize gray code tables
        num_bits_per_device = len(list(devices.values())[0])
        all_codes = generate_gray_codes(num_bits_per_device)
        self.gray_code_to_integer_map = dict((code, idx) for idx, code in enumerate(all_codes))
        self.num_codes = len(all_codes)

    def start(self, on_device_angle_changed):
        self._on_device_angle_changed = on_device_angle_changed
        current_sensor_values = self.sensors_adapter.start(self._on_sensor_values)
        self.current_positions = self._decode_values(current_sensor_values)
        now = self.clock.now()
        for device in self.current_positions.keys():
            self.last_position_ts[device] = now
        return self.current_positions

    def stop(self):
        self.sensors_adapter.stop()

    def get_current_position(self, device):
        return self.current_positions[device]

    def get_current_positions(self):
        return self.current_positions

    def _on_sensor_values(self, values):
        positions = {}
        speeds = {}
        now = self.clock.now()
        for device, position in self._decode_values(values).items():
            last_position = self.current_positions[device]
            if position != last_position:
                positions[device] = position
                last_position_ts = self.last_position_ts.get(device, None)
                speed = None
                if last_position_ts:
                    elapsed_time_since_last_read = now - last_position_ts
                    if elapsed_time_since_last_read < self.stasis_timeout:
                        speed = self._calculate_angular_speed(last_position, position, elapsed_time_since_last_read)
                if speed and speed > self.max_speed:
                    self.log_error_message('Speed too high ({0} deg/sec). Probably the result of a faulty sensor read on the shaft encoder.'.format(speed))
                    return
                speeds[device] = speed
            self.last_position_ts[device] = now
            self.current_positions[device] = position
        if len(positions) > 0:
            self._on_device_angle_changed(positions, speeds)

    def _decode_values(self, values):
        result = {}
        for device, sensor_indexes in self.devices.items():
            sensor_values = [values[idx] for idx in sensor_indexes]
            position = self._code_to_position(sensor_values)
            result[device] = position
        return result

    def _code_to_position(self, code):
        code_str = ''.join(code)
        value = self.gray_code_to_integer_map[code_str]
        angle = 360.0 - 360.0 / self.num_codes * value
        return WheelPosition(value, angle, code_str)

    def _calculate_angular_speed(self, old_position, new_position, elapsed_time):
        angle_diff_a = new_position.angle - old_position.angle
        angle_diff_b = old_position.angle - new_position.angle
        if angle_diff_a < 0:
            angle_diff_a += 360.0
        if angle_diff_b < 0:
            angle_diff_b += 360.0
        # Choose the minimum of the two angles
        minimum_angle_diff = min(angle_diff_a, angle_diff_b)
        return minimum_angle_diff / elapsed_time.total_seconds()  # Degrees per second


if __name__ == '__main__':
    def main():
        from .sensors_adapter import GPIOSensorsAdapter
        from time import sleep
        from ..clock import Clock

        clock = Clock()

        adapter = GPIOSensorsAdapter([11, 9, 10, 22, 27, 17], 5)

        def print_values(positions, speeds=None):
            print('Positions: {0} Speeds: {1}'.format(positions, speeds))
        shaft_encoders = ShaftEncoders(adapter, {'A': [0, 1, 2, 3, 4]}, clock, 1.0, 800, print)
        current_values = shaft_encoders.start(print_values)
        print_values(current_values)
        try:
            while True:
                sleep(1)
        except:
            pass
        shaft_encoders.stop()
    main()
