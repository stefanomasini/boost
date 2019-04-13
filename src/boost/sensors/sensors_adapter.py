from RPi import GPIO


class GPIOSensorsAdapter(object):
    def __init__(self, sensor_pins, bouncetime, on_edge_callback):
        self.sensor_pins = sensor_pins
        self.sensors_mapping = {}
        for device, pins in sensor_pins.items():
            for sensor_idx, sensor_pin in enumerate(pins):
                self.sensors_mapping[sensor_pin] = (device, sensor_idx)
        self.bouncetime = bouncetime
        self.on_edge_callback = on_edge_callback
        self.previous_sensor_values = {}

    def read_all_sensor_values(self):
        return dict((device, [self._read_sensor(sensor_pin) for sensor_pin in sensor_pins]) for device, sensor_pins in self.sensor_pins.items())

    def start(self):
        GPIO.setmode(GPIO.BCM)
        for sensor_pin in self.sensors_mapping.keys():
            GPIO.setup(sensor_pin, GPIO.IN)
            GPIO.add_event_detect(sensor_pin, GPIO.BOTH, callback=self._on_edge, bouncetime=self.bouncetime)

    def stop(self):
        GPIO.cleanup()

    def _on_edge(self, sensor_pin):
        current_value = self._read_sensor(sensor_pin)
        if current_value != self.previous_sensor_values[sensor_pin]:
            self.on_edge_callback(*self.sensors_mapping[sensor_pin], current_value)
        self.previous_sensor_values[sensor_pin] = current_value

    def _read_sensor(self, sensor_pin):
        # The sensor returns a high value (1) for black, and a low value (0) for white, which is what we want
        # But the actual LED on the sensor is ON for white (i.e. 0) and OFF for black (i.e. 1)
        return str(GPIO.input(sensor_pin))


if __name__ == '__main__':
    from time import sleep
    def callback(device, sensor_idx, value):
        print('Sensor {0} {1} {2}'.format(device, sensor_idx, value))
    adapter = GPIOSensorsAdapter({'A': [9, 11]}, 20, callback)
    adapter.start()
    for _device, _value in adapter.read_all_sensor_values().items():
        print('Current value, {0}: {1}'.format(_device, _value))
    try:
        while True:
            sleep(1)
    except:
        pass
    adapter.stop()
