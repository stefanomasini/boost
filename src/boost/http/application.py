import json
import asyncio


def create_http_app(storage, http_server_input_message_queue, get_compilation_errors_for_json, is_program_running, run_program, stop_program, device_names):
    from quart import Quart, websocket, request, jsonify, Response

    app = Quart('boost')

    @app.route('/')
    async def hello_world():
        return 'Home'

    @app.route('/whole_state')
    async def whole_state():
        return jsonify({
            'programs': storage.get_programs(),
            'compilation_errors': get_compilation_errors_for_json()['errors'],
            'program_running': is_program_running(),
            'auto_run': storage.get_auto_run(),
            'device_names': device_names,
        })

    @app.route('/command/savePrograms', methods=['POST'])
    async def command_save_programs():
        programs = await request.json
        ok = storage.set_programs(programs)
        if ok:
            return Response('Ok', mimetype='text/plain')
        else:
            return Response('Compilation errors', status=400, mimetype='text/plain')

    @app.route('/command/runProgram', methods=['POST'])
    async def command_run_program():
        ok = run_program()
        if ok:
            return Response('Ok', mimetype='text/plain')
        else:
            return Response('Compilation errors', status=400, mimetype='text/plain')

    @app.route('/command/stopProgram', methods=['POST'])
    async def command_stop_program():
        stop_program()
        return Response('Ok', mimetype='text/plain')

    @app.route('/command/setAutoRun', methods=['POST'])
    async def command_set_auto_run():
        data = await request.json
        result = storage.set_auto_run(data)
        return jsonify(result)

    async def ws_sending():
        while True:
            msg = await http_server_input_message_queue.get_next_message()
            await websocket.send(json.dumps(msg))

    async def ws_receiving():
        while True:
            data = await websocket.receive()
            print(f'received: {data}')

    @app.websocket('/websocket')
    async def ws():
        producer = asyncio.create_task(ws_sending())
        consumer = asyncio.create_task(ws_receiving())
        await asyncio.gather(producer, consumer)

    return app


def run_http_app(app, host, port):
    from hypercorn.config import Config as HyperConfig
    from hypercorn.asyncio import serve
    from quart.logging import create_serving_logger

    config = HyperConfig()
    config.access_log_format = "%(h)s %(r)s %(s)s %(b)s %(D)s"
    config.access_logger = create_serving_logger()  # type: ignore
    config.bind = [f"{host}:{port}"]
    config.ca_certs = None
    config.certfile = None
    # config.debug = True
    config.error_logger = config.access_logger  # type: ignore
    config.keyfile = None
    config.use_reloader = False
    scheme = 'https' if config.ssl_enabled else 'http'
    print("Listening on {}://{}".format(scheme, config.bind[0]))
    return serve(app, config)
