class Planner(object):
    def __init__(self, shaft_encoder, motors_controller):
        self.shaft_encoder = shaft_encoder
        self.motors_controller = motors_controller
        self.current_target_position = {}
        self.constants = None

    def set_constants(self, constants):
        self.constants = constants

    def on_shaft_position(self, positions, speeds):
        for device, position in positions.items():
            target_position = self.current_target_position.get(device, None)
            if target_position:
                if position.position == target_position:
                    self.motors_controller.set_target_speed(device, 0, self.constants)

    def set_plan(self, device, target_position, speed, direction):
        assert device in self.shaft_encoder.devices, 'Invalid device {0}'.format(device)
        assert direction in ('cw', 'ccw'), 'Invalid direction {0}'.format(direction)
        assert speed > 0, 'Speed must be a positive value'

        # positive speed = Counter-Clockwise (CCW) rotation
        # negative speed = Clockwise (CW) rotation
        if direction == 'cw':
            speed = -speed

        self.current_target_position[device] = target_position
        if self.shaft_encoder.get_current_position(device).position != target_position:
            self.motors_controller.set_target_speed(device, speed, self.constants)
