from .http.application import create_http_app, run_http_app
from .storage import Storage, SAMPLE_PROGRAM
from .sensors.shaft_encoder import ShaftEncoders
from .motors.motors_controller import MotorsController
from .planner import Planner
from .clock import Clock
from .language.parser import parse_program
from .executor import ExecutionContext, WarningRuntimeMessage
from .constants import RuntimeParameters
import asyncio


class HttpServerInputMessageQueue(object):
    def __init__(self, asyncio_loop):
        self.asyncio_loop = asyncio_loop
        self.msg_queue = asyncio.Queue()

    def send_message(self, **kwargs):
        """
        Send a message to the asyncio-based http server from an external thread.
        """
        coro = self.msg_queue.put(kwargs)
        asyncio.run_coroutine_threadsafe(coro, self.asyncio_loop)

    async def get_next_message(self):
        """
        Fetch the next message from the queue. Wait until a message is available.
        To be called only from the main asyncio-based thread.
        """
        return await self.msg_queue.get()


class Motor(object):
    def __init__(self, device, planner, log_message):
        self.device = device
        self.planner = planner
        self.log_message = log_message

    def turn(self, direction, to, speed):
        self.planner.set_plan(self.device, to, speed, 'cw' if direction == 'left' else 'ccw')
        if to:
            self.log_message('{0} turning {1} to {2} at speed {3}'.format(self.device, direction, to, speed))
        else:
            self.log_message('{0} turning {1} at speed {2}'.format(self.device, direction, speed))

    def stop(self):
        self.planner.set_stop_plan(self.device)
        self.log_message('{0} stopping'.format(self.device))


def build_hardare_adapters(config):
    if getattr(config, 'mock_hardware', False):
        from .sensors.sensors_mock import MockSensorsAdapter
        from .motors.motors_mock import MockMotorsAdapter
        sensors_adapter = MockSensorsAdapter(config.sensor_pins)
        motors_adapter = MockMotorsAdapter(print)
    else:
        from .sensors.sensors_adapter import GPIOSensorsAdapter
        from .motors.motors_adapter import ThunderBorgAdapter
        sensors_adapter = GPIOSensorsAdapter(config.sensor_pins, config.gpio_read_delay_in_ms)
        motors_adapter = ThunderBorgAdapter(print)
    return sensors_adapter, motors_adapter


class Application(object):
    def __init__(self, config):
        self.config = config
        self.clock = Clock()
        self.storage = Storage({})
        self.sensors_adapter, self.motors_adapter = build_hardare_adapters(config)
        self.shaft_encoder = ShaftEncoders(self.sensors_adapter, config.sensor_devices, self.clock, config.stasis_timeout_in_sec, config.max_speed_in_deg_per_sec, print)
        self.motors_controller = MotorsController(self.clock, config.sensor_devices.keys())
        self.planner = Planner(self.shaft_encoder, self.motors_controller)
        self.symbols = {'A': Motor('A', self.planner, self.log_message), 'B': Motor('B', self.planner, self.log_message)}
        self.loop = asyncio.get_event_loop()
        self.http_server_input_message_queue = HttpServerInputMessageQueue(self.loop)
        device_names = list(config.sensor_devices.keys())
        self.http_app = create_http_app(self.storage, self.http_server_input_message_queue, self.get_compilation_errors_for_json,
                                        self.is_program_running, self.run_program, self.stop_program, device_names, self.set_motor_power, self.reset_motors)
        self.execution_context = None

    def run(self):
        print('Starting up application.')
        self.start_everything()
        print('CTRL + C to quit.')
        # loop.set_debug(config.debug)
        self.loop.run_until_complete(self.run_asyncio_tasks())
        print('Signal intercepted. Shutting down application...')
        self.stop_everything()
        print('... shutdown terminated.')

    def start_everything(self):
        self.storage.initialize(self.on_program_changed)
        self.planner.set_constants(self.storage.get_motors_constants())
        if not self.motors_adapter.initialize():
            raise Exception('Error initializing the ThunderBorgAdapter')
        self.shaft_encoder.start(self.planner.on_shaft_position)
        self.compile_program()
        if self.storage.should_auto_run_current_program():
            self.run_program()
        else:
            self.compile_program()

    def stop_everything(self):
        self.motors_adapter.stop()
        self.shaft_encoder.stop()

    def _compile_program(self):
        program_code = self.storage.get_current_program()['code']
        errors = []
        motors_constants = self.storage.get_motors_constants()
        runtime_parameters = RuntimeParameters(self.shaft_encoder.num_codes, len(motors_constants.power_definitions))
        program = parse_program(program_code, self.symbols.keys(), runtime_parameters, errors)
        return program, errors

    def compile_program(self):
        program, errors = self._compile_program()
        if errors:
            self.on_compilation_errors(errors)
        else:
            return program

    def get_compilation_errors_for_json(self):
        _, errors = self._compile_program()
        return self._format_compilation_errors_for_json(errors)

    def _format_compilation_errors_for_json(self, errors):
        return {'errors': [error.to_json() for error in errors]}

    def log_message(self, message):
        print(message)
        self.send_redux_message('SERVER_LOG', message)

    def on_compilation_errors(self, errors):
        for error in errors:
            print(error.pretty_print())
        self.send_redux_message('COMPILATION_ERRORS', self._format_compilation_errors_for_json(errors))

    def on_runtime_error(self, message):
        print('RUNTIME ERROR:', message)
        self.send_redux_message('RUNTIME_ERROR', message)

    def on_program_changed(self):
        return self.compile_program() is not None

    def send_redux_message(self, type, payload):
        self.http_server_input_message_queue.send_message(type=type, payload=payload)

    def set_motor_power(self, device, power):
        if not self.is_program_running():
            self.motors_controller.set_power_manually(device, power)

    def reset_motors(self):
        if not self.is_program_running():
            self.motors_controller.stop_all_motors(self.storage.get_motors_constants())

    async def apply_motor_power_task(self):
        while True:
            self.motors_controller.apply_motor_power(self.motors_adapter)
            await asyncio.sleep(self.config.motors_apply_power_every_ms / 1000.0)

    def run_program(self):
        program = self.compile_program()
        if program:
            self.execution_context = ExecutionContext(program, self.clock, self.symbols, self.on_runtime_error)
            self.log_message('Program started')
            return True
        else:
            return False

    def stop_program(self):
        if self.is_program_running():
            self.cleanup_terminated_program()

    def is_program_running(self):
        return self.execution_context is not None and not self.execution_context.terminated

    async def report_hardware_levels_task(self):
        previous_motor_values = {}
        previous_shaft_values = {}
        while True:
            for device, power in self.motors_controller.get_current_power().items():
                previous_value = previous_motor_values.get(device, None)
                if power != previous_value:
                    self.send_redux_message('MOTOR_POWER', {'device': device, 'power': power})
                previous_motor_values[device] = power
            for device, position in self.shaft_encoder.get_current_positions().items():
                previous_value = previous_shaft_values.get(device, None)
                if position != previous_value:
                    self.send_redux_message('SHAFT_POSITION', {'device': device, 'position': position.position, 'angle': position.angle})
                previous_shaft_values[device] = position
            await asyncio.sleep(self.config.monitor_motors_power_every_ms / 1000.0)

    def cleanup_terminated_program(self):
        self.log_message('Program terminated')
        self.send_redux_message('SET_PROGRAM_RUNNING', False)
        self.execution_context = None
        self.motors_controller.stop_all_motors(self.storage.get_motors_constants())

    async def execute_program_task(self):
        while True:
            if self.is_program_running():
                self.execution_context.execute_if_scheduled()
                if self.execution_context.terminated:
                    self.cleanup_terminated_program()
            await asyncio.sleep(self.config.step_program_every_ms / 1000.0)

    async def run_asyncio_tasks(self):
        await asyncio.wait([
            run_http_app(self.http_app, '0.0.0.0', self.config.server_port),
            asyncio.create_task(self.apply_motor_power_task()),
            asyncio.create_task(self.execute_program_task()),
            asyncio.create_task(self.report_hardware_levels_task()),
        ], return_when=asyncio.FIRST_COMPLETED)

