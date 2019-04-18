from .http.application import create_http_app, run_http_app
from .storage import Storage
from .sensors.sensors_adapter import GPIOSensorsAdapter
from .sensors.shaft_encoder import ShaftEncoders
from .motors.motors_controller import MotorsController
from .motors.motors_adapter import ThunderBorgAdapter
from .planner import Planner
from .clock import Clock
from .language.parser import parse_program
from .executor import ExecutionContext, WarningRuntimeMessage
import asyncio


class HttpServerInputMessageQueue(object):
    def __init__(self, asyncio_loop):
        self.msg_queue = asyncio.Queue()
        self.asyncio_loop = asyncio_loop

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
    def __init__(self, device, planner):
        self.device = device
        self.planner = planner

    def turn(self, direction, to, speed):
        self.planner.set_plan(self.device, to, speed, 'cw' if direction == 'left' else 'ccw')


def run_application(config):
    clock = Clock()

    storage = Storage({})
    storage.initialize()

    sensors_adapter = GPIOSensorsAdapter(config.sensor_pins, config.gpio_read_delay_in_ms)
    shaft_encoder = ShaftEncoders(sensors_adapter, config.sensor_devices, clock, config.stasis_timeout_in_sec, config.max_speed_in_deg_per_sec, print)

    motors_adapter = ThunderBorgAdapter(print)
    motors_controller = MotorsController(clock, config.sensor_devices.keys())

    planner = Planner(shaft_encoder, motors_controller)
    planner.set_constants(storage.get_motors_constants())

    if not motors_adapter.initialize():
        raise Exception('Error initializing the ThunderBorgAdapter')

    shaft_encoder.start(planner.on_shaft_position)

    async def apply_motor_power_task():
        while True:
            motors_controller.apply_motor_power(motors_adapter)
            await asyncio.sleep(config.motors_apply_power_every_ms / 1000.0)

    program_code = storage.get_current_program()['code']
    symbols = {'A': Motor('A', planner), 'B': Motor('B', planner)}
    errors = []
    program = parse_program(program_code, symbols.keys(), errors)
    assert len(errors) == 0, 'Errors in program!'
    execution_context = ExecutionContext(program, clock, symbols, lambda m: print('RUNTIME ERROR', m.message))

    async def execute_program_task():
        while True:
            if execution_context and not execution_context.terminated:
                execution_context.execute_if_scheduled()
            await asyncio.sleep(config.step_program_every_ms / 1000.0)

    def stop_everything():
        motors_adapter.stop()
        shaft_encoder.stop()

    # ------

    loop = asyncio.get_event_loop()

    http_server_input_message_queue = HttpServerInputMessageQueue(loop)

    def send_redux_message(type, payload):
        http_server_input_message_queue.send_message(type=type, payload=payload)

    # async def test_producer():
    #     while True:
    #         send_redux_message('TEST_MESSAGE', {'foo': 'bar'})
    #         await asyncio.sleep(1)

    async def run_asyncio_tasks():
        http_app = create_http_app(storage, http_server_input_message_queue)
        http_app_task = run_http_app(http_app, '127.0.0.1', config.server_port)

        await asyncio.wait([
            http_app_task,
            asyncio.create_task(apply_motor_power_task()),
            asyncio.create_task(execute_program_task()),
            # asyncio.create_task(test_producer()),
        ], return_when=asyncio.FIRST_COMPLETED)

    print('CTRL + C to quit.')

    # loop.set_debug(config.debug)
    loop.run_until_complete(run_asyncio_tasks())

    print('Signal intercepted. Exiting program.')

    stop_everything()
