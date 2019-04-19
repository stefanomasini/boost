
class MockSensorsAdapter(object):
    def __init__(self, sensor_pins):
        self.sensor_pins = sensor_pins
        self.on_edge_callback = None
        self.sensor_values = None

    def start(self, on_edge_callback):
        self.on_edge_callback = on_edge_callback
        self.sensor_values = [self._read_sensor(sensor_pin) for sensor_pin in self.sensor_pins]
        return self.sensor_values

    def stop(self):
        pass

    def _read_sensor(self, sensor_pin):
        return '0'

