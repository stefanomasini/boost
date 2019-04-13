from .sensors_adapter import GPIOSensorsAdapter
from ..gray_code import generate_gray_codes


class ShaftEncoders(object):
    def __init__(self, num_bits_per_device, sensor_pins_msb_first, bouncetime, on_device_angle_changed):
        self.sensor_pins_msb = sensor_pins_msb_first
        self._on_device_angle_changed = on_device_angle_changed
        for device, sensor_pins in sensor_pins_msb_first.items():
            assert len(sensor_pins) == num_bits_per_device, \
                'Device {0} has wrong number of sensor_pins ({1} instead of {2})'.format(device, len(sensor_pins), num_bits_per_device)
        all_codes = generate_gray_codes(num_bits_per_device)
        self.gray_code_to_integer_map = dict((code, idx) for idx, code in enumerate(all_codes))
        self.num_codes = len(all_codes)
        self.adapter = GPIOSensorsAdapter(sensor_pins_msb_first, bouncetime, self._on_sensor_value)
        self.current_values = {}

    def start(self):
        self.adapter.start()
        self.current_values = self.adapter.read_all_sensor_values()
        return dict((device, self._code_to_angle(code)) for device, code in self.current_values.items())

    def stop(self):
        self.adapter.stop()

    def _on_sensor_value(self, device, bit_position, value):
        self.current_values[device][bit_position] = value
        self._on_device_angle_changed(device, self._code_to_angle(self.current_values[device]))

    def _code_to_angle(self, code):
        value = self.gray_code_to_integer_map[''.join(code)]
        return 360.0 / self.num_codes * value


if __name__ == '__main__':
    from time import sleep

    def callback(device, angle):
        print('Device {0} {1}'.format(device, angle))
    shaft_encoders = ShaftEncoders(2, {'A': [9, 11]}, 20, callback)
    current_values = shaft_encoders.start()
    for _device, _angle in current_values.items():
        print('Current value, {0}: {1}'.format(_device, _angle))
    try:
        while True:
            sleep(1)
    except:
        pass
    shaft_encoders.stop()
