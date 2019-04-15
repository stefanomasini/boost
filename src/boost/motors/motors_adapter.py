from boost.motors import ThunderBorg


class ThunderBorgAdapter(object):
    def __init__(self, log_message):
        self.log_message = log_message
        self.TB = ThunderBorg.ThunderBorg()
        self.TB.printFunction = log_message

    def initialize(self):
        # Set the board up (checks the board is connected)
        self.TB.Init()
        if not self.TB.foundChip:
            boards = ThunderBorg.ScanForThunderBorg()
            if len(boards) == 0:
                self.log_message('No ThunderBorg found, check you are attached')
            else:
                self.log_message('No ThunderBorg at address %02X, but we did find boards:' % self.TB.i2cAddress)
                for board in boards:
                    self.log_message('    %02X (%d)' % (board, board))
                self.log_message('If you need to change the I²C address change the setup line so it is correct, e.g.')
                self.log_message('TB.i2cAddress = 0x%02X' % boards[0])
            return False
        else:
            # Enable the communications failsafe
            # The failsafe will turn the motors off unless it is commanded at least once every 1/4 of a second
            self.TB.SetCommsFailsafe(True)

    def is_faulty(self):
        faulty_1 = self.TB.GetDriveFault1()
        faulty_2 = self.TB.GetDriveFault2()
        if faulty_1:
            self.log_message('Motor A is faulty')
        if faulty_2:
            self.log_message('Motor B is faulty')
        return faulty_1 or faulty_2

    def get_voltage_reading(self):
        return self.TB.GetBatteryReading()

    def set_motor_speed(self, motor, speed):
        assert motor in ('A', 'B'), 'Unknown motor {0}'.format(motor)
        if motor == 'A':
            self.TB.SetMotor1(speed)
        if motor == 'B':
            self.TB.SetMotor2(speed)


if __name__ == '__main__':
    adapter = ThunderBorgAdapter(print)

    # ThunderBorg.ScanForThunderBorg(busNumber=1)

    adapter.initialize()
    print('is_faulty', adapter.is_faulty())
    print('get_voltage_reading', adapter.get_voltage_reading())
