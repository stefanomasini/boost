
class MockMotorsAdapter(object):
    def __init__(self, log_message):
        self.log_message = log_message

    def initialize(self):
        return True

    def is_faulty(self):
        return False

    def get_voltage_reading(self):
        return 12.0

    def set_motor_power(self, motor, power):
        pass

    def stop(self):
        pass

