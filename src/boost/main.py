from .http.application import create_http_app, run_http_app
from .storage import Storage
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


def run_application(config):
    loop = asyncio.get_event_loop()

    http_server_input_message_queue = HttpServerInputMessageQueue(loop)

    def send_redux_message(type, payload):
        http_server_input_message_queue.send_message(type=type, payload=payload)

    async def test_producer():
        while True:
            send_redux_message('TEST_MESSAGE', {'foo': 'bar'})
            await asyncio.sleep(1)

    storage = Storage({})
    storage.initialize()

    async def run_asyncio_tasks():
        http_app = create_http_app(storage, http_server_input_message_queue)
        http_app_task = run_http_app(http_app, '127.0.0.1', config.server_port)

        test_task = asyncio.create_task(test_producer())
        await asyncio.wait([http_app_task, test_task], return_when=asyncio.FIRST_COMPLETED)

    print('CTRL + C to quit.')

    # loop.set_debug(config.debug)
    loop.run_until_complete(run_asyncio_tasks())

    print('Signal intercepted. Exiting program.')
