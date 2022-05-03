import aiohttp
import asyncio
import pika
import random
import traceback
import uuid

from aiohttp import web
from functools import wraps, partial
from typing import List, Dict


class Server:
    __asyncSession: aiohttp.ClientSession
    __pikaConnection: pika.BlockingConnection
    __pikaChannel: pika.adapters.blocking_connection.BlockingChannel
    routes: List[web.RouteDef]

    def __init__(self):
        print("Init Handler")
        self.__asyncSession = None
        self.__pikaConnection = None
        self.__pikaChannel = None
        self.init_routes()
        pass

    def init_routes(self) -> None:
        self.routes = [
            web.get('/', self.proc_get_req),
            web.post('/', self.proc_post_req),
        ]
        return

    async def __getAsyncSession(self) -> aiohttp.ClientSession:
        if isinstance(self.__asyncSession, aiohttp.ClientSession) and not self.__asyncSession.closed:
            return self.__asyncSession
        self.__asyncSession = aiohttp.ClientSession()
        return self.__asyncSession

    async def __getPikaConnection(self) -> pika.BlockingConnection:
        if isinstance(self.__pikaConnection, pika.BlockingConnection) and not self.__pikaConnection.is_closed:
            return self.__pikaConnection
        host = await self.__getServices(value_pattern = "rabbitmq")
        print(host)
        self.__pikaConnection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host["rabbitmq"].lstrip("http://"))
        )
        return self.__pikaConnection

    async def __getPikaChannel(self) -> pika.adapters.blocking_connection.BlockingChannel:
        if isinstance(self.__pikaChannel,
                      pika.adapters.blocking_connection.BlockingChannel) and not self.__pikaChannel.is_closed:
            return self.__pikaChannel
        connection = await self.__getPikaConnection()
        self.__pikaChannel = connection.channel()
        self.__pikaChannel.queue_declare(queue='lab5')
        return self.__pikaChannel

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
                resp_json[key] = f"http://{value['Address']}:{value['Port']}"
        return resp_json

    async def proc_get_req(self, request: web.Request) -> None:
        session = await self.__getAsyncSession()
        services = await self.__getServices()
        #message_services = list((await self.__getServices(services, 'message')).values())
        log_services = list((await self.__getServices(services, 'logging')).values())

        print("GET-request is sent to logging service")

        uuid_generation = {
            "uuid": str(uuid.uuid4()),
            "msg": (await request.json()).get('msg')
        }

        async with session.get(
        url=f"{random.choice(log_services)}/logging",
        json=uuid_generation
        ) as log_resp:
            log_resp_info = await log_resp.read()
        print('Info received from logging service:', log_resp_info.decode())

        async with session.get(
        url=f"{random.choice(message_services)}/messages",
        json=uuid_generation
        ) as message_resp:
            message_resp_info = await message_resp.read()
        print('Info received from message service:', message_resp_info.decode())

        resp = web.StreamResponse()
        resp.set_status(200)
        await resp.prepare(request)
        await resp.write_eof(message_resp_info)

        return

    async def proc_post_req(self, request: web.Request) -> None:
        session = await self.__getAsyncSession()
        services = await self.__getServices()
        log_services = list((await self.__getServices(services, 'logging')).values())

        print("POST-request is sent to logging service")
        try:
            msg = (await request.json()).get('msg')
            uuid_generation = {
                "uuid": str(uuid.uuid4()),
                "msg": msg
            }

            async with session.post(
                    url=f"{random.choice(log_services)}/logging",
                    json=uuid_generation
            ) as log_resp:
                await log_resp.read()
            print('Info received from logging service:', log_resp.status)

            await self.sendPika(msg)
            print(f" [x] Sent to message queue: {msg}")

            resp = web.StreamResponse()
            resp.set_status(200)
            await resp.prepare(request)
            await resp.write_eof()

        except Exception as ex:
            traceback.print_exc()
            print(ex)

            resp = web.StreamResponse()
            resp.set_status(500)
            await resp.prepare(request)
            await resp.write_eof()
        return

    async def sendPika(self, msg) -> None:
        channel = await self.__getPikaChannel()
        await self.pikaChannelSend(channel, msg)
        return

    async def close(self) -> None:
        if self.__asyncSession and not self.__asyncSession.closed:
            await self.__asyncSession.close()
        if self.__pikaConnection and not self.__pikaConnection.is_closed:
            self.__pikaConnection.close()
        return

    def async_wrap(func):
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if loop is None:
                loop = asyncio.get_event_loop()
            partial_func = partial(func, *args, **kwargs)
            return await loop.run_in_executor(executor, partial_func)
        return run

    @async_wrap
    def pikaChannelSend(self, channel: pika.adapters.blocking_connection.BlockingChannel, msg):
        channel.basic_publish(exchange='', routing_key='lab5', body=msg)
        return


def main():
    srv = Server()
    app = web.Application()
    app.add_routes(srv.routes)
    web.run_app(app=app, port=80)


if __name__ == "__main__":
    main()
