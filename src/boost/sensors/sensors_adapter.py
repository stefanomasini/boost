from RPi import GPIO
import time


class GPIOSensorsAdapter(object):
    def __init__(self, sensor_pins, read_delay):
        self.sensor_pins = sensor_pins
        self.sensor_indexes = dict([(sensor_pin, idx) for idx, sensor_pin in enumerate(sensor_pins)])
        self.read_delay = read_delay
        self.on_edge_callback = None
        self.sensor_values = None

    def start(self, on_edge_callback):
        self.on_edge_callback = on_edge_callback
        GPIO.setmode(GPIO.BCM)
        for sensor_pin in self.sensor_pins:
            GPIO.setup(sensor_pin, GPIO.IN)
        self.sensor_values = [self._read_sensor(sensor_pin) for sensor_pin in self.sensor_pins]
        for sensor_pin in self.sensor_pins:
            GPIO.add_event_detect(sensor_pin, GPIO.BOTH, callback=self._on_edge)
        return self.sensor_values

    def stop(self):
        GPIO.cleanup()

    def _on_edge(self, sensor_pin):
        if not self.sensor_values:
            return
        # Wait for a small delay before reading the sensor, as it seems to be more reliable
        # Source: https://raspberrypi.stackexchange.com/a/49692
        time.sleep(self.read_delay / 1000.0)
        current_value = self._read_sensor(sensor_pin)
        sensor_pin_idx = self.sensor_indexes[sensor_pin]
        call_callback = current_value != self.sensor_values[sensor_pin_idx]
        self.sensor_values[sensor_pin_idx] = current_value
        if call_callback:
            self.on_edge_callback(self.sensor_values)

    def _read_sensor(self, sensor_pin):
        # The sensor returns a high value (1) for black, and a low value (0) for white, which is what we want
        # But the actual LED on the sensor is ON for white (i.e. 0) and OFF for black (i.e. 1)
        return str(GPIO.input(sensor_pin))


if __name__ == '__main__':
    def print_values(sensor_values):
        print('Sensors: {0}'.format(''.join([('.' if v == '1' else 'O') for v in sensor_values])))
    adapter = GPIOSensorsAdapter([11, 9, 10, 22, 27, 17, 14, 15, 18, 25, 8, 7], 5)
    initial_values = adapter.start(print_values)
    print_values(initial_values)
    try:
        while True:
            time.sleep(1)
    except:
        pass
    adapter.stop()
