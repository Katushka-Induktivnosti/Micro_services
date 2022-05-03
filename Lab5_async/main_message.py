import pika
import threading
import typing

from aiohttp import web
from typing import List, Dict


class Server:
    msg: typing.List
    msg_lock: threading.Lock
    routes: typing.List[web.RouteDef]
    queue_thread: threading.Thread

    def __init__(self):
        self.msg = []
        self.msg_lock = threading.Lock()
        self.init_routes()

    def init_routes(self):
        self.routes = [
            web.get('/messages', self.proc_get_req),
        ]
        return

    def runQueue(self):
        self.queue_thread = threading.Thread(target=self.__queue)
        self.queue_thread.start()

    def __queue(self):
        rabbitmq = self.__getServices()
        host = list((self.__getServices(rabbitmq, 'rabbitmq')).values())
        connection = pika.BlockingConnection(pika.ConnectionParameters(host= self.__getServices()))
        channel = connection.channel()
        channel.queue_declare(queue='lab5')

        def callback(ch, method, properties, body):
            with self.msg_lock:
                self.msg.append(body.decode())
            print(f" [x] Received {self.msg[-1]}")
            print(','.join(self.msg))

        channel.basic_consume(queue='lab5', on_message_callback=callback, auto_ack=True)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
        connection.close()
        return

    async def __getServices(self, input_json: Dict = None, value_pattern: str = None) -> Dict:
        if input_json:
            resp_json = input_json.copy()
        else:
            session = await self.__getAsyncSession()
            async with session.get(
                    url="http://192.168.111.4:8500/v1/agent/services"
            ) as resp:
                resp_json = await resp.json()
        for key, value in (resp_json.copy()).items():
            if isinstance(value_pattern, str):
                if value_pattern not in key:
                    resp_json.pop(key)
            if isinstance(value, Dict):
                resp_json[key] = f"{value['Address']}:{value['Port']}"
        return resp_json

    async def proc_get_req(self, request: web.Request) -> None:
        wiped_msg = []
        with self.msg_lock:
            if len(self.msg) >= 5:
                wiped_msg = self.msg.copy()
                self.msg.clear()
        if wiped_msg:
            resp = web.StreamResponse()
            resp.set_status(200)
            await resp.prepare(request)
            await resp.write_eof((','.join(wiped_msg)).encode())
            return
        else:
            resp = web.StreamResponse()
            resp.set_status(200)
            await resp.prepare(request)
            await resp.write_eof("Not enough messages".encode())
            return


def main():
    srv = Server()
    app = web.Application()
    app.add_routes(srv.routes)
    srv.runQueue()
    web.run_app(app=app, port=81)


if __name__ == '__main__':
    main()
