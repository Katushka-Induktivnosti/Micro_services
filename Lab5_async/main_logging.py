import asyncio
import hazelcast
import traceback
import typing
import aiohttp
import requests

from typing import List, Dict
from aiohttp import web
from functools import wraps, partial
from hazelcast.proxy.map import BlockingMap
from hazelcast.types import KeyType, ValueType


class Server:
    __clientHazelcast: hazelcast.HazelcastClient
    __mapHazelcast: BlockingMap[KeyType, ValueType]
    routes: typing.List[web.RouteDef]

    def __init__(self):
        self.__clientHazelcast = None
        self.__asyncSession = None
        self.__mapHazelcast = None
        self.init_routes()
        return

    def init_routes(self) -> None:
        self.routes = [
            web.get('/logging', self.proc_get_req),
            web.post('/logging', self.proc_post_req),
        ]
        return

    def __getClientHazelcast(self) -> hazelcast.HazelcastClient:
        if isinstance(self.__clientHazelcast, hazelcast.HazelcastClient):
            return self.__clientHazelcast
        self.__clientHazelcast = hazelcast.HazelcastClient(cluster_members=(self.hazelcast_conf()))
        return self.__clientHazelcast

    def __getMapHazelcast(self) -> BlockingMap[KeyType, ValueType]:
        if isinstance(self.__mapHazelcast, BlockingMap):
            return self.__mapHazelcast
        self.__mapHazelcast = (self.__getClientHazelcast()).get_map("lab5_map").blocking()
        return self.__mapHazelcast

    async def proc_post_req(self, request: web.Request) -> None:
        data = await request.json()
        print('Received request: ', data)
        try:
            await self.map_set(data["uuid"], data["msg"])
            print("Saved to hazelcast map")
            resp = web.StreamResponse()
            resp.set_status(200)
            await resp.prepare(request)
            await resp.write_eof()
        except Exception as ex:
            traceback.print_exc()
            print(ex)
            print('Message cannot be saved to hazelcast map')
            resp = web.StreamResponse()
            resp.set_status(500)
            await resp.prepare(request)
            await resp.write_eof()
        return

    async def proc_get_req(self, request: web.Request) -> None:      
        data = await request.json()
        print('Received request: ', data)
        try:
            print('Return messages: ', await self.map_values())
            all_map = all_map = ','.join((await self.map_get_all(await self.map_key_set())).values())
            resp = web.StreamResponse()
            resp.set_status(200)
            await resp.prepare(request)
            await resp.write_eof(all_map.encode())
        except Exception as ex:
            traceback.print_exc()
            print(ex)
            resp = web.StreamResponse()
            resp.set_status(500)
            await resp.prepare(request)
            await resp.write_eof()
        return

    def __getServices(self, input_json: Dict = None, value_pattern: str = None) -> Dict:
        if input_json:
            resp_json = input_json.copy()
        else:
            resp = requests.get(
                    url="http://192.168.111.4:8500/v1/agent/services"
            )
            resp_json = resp.json()
        for key, value in (resp_json.copy()).items():
            if isinstance(value_pattern, str):
                if value_pattern not in key:
                    resp_json.pop(key)
            if isinstance(value, Dict):
                resp_json[key] = f"{value['Address']}:{value['Port']}"
        return resp_json

    def async_wrap(func):
        @wraps(func)
        async def run(*args, loop=None, executor=None, **kwargs):
            if loop is None:
                loop = asyncio.get_event_loop()
            partial_func = partial(func, *args, **kwargs)
            return await loop.run_in_executor(executor, partial_func)
        return run

    @async_wrap
    def map_set(self, *args) -> None:
        map_hz = self.__getMapHazelcast()
        return map_hz.set(*args)

    @async_wrap
    def map_values(self, *args) -> typing.List[ValueType]:
        map_hz = self.__getMapHazelcast()
        return map_hz.values(*args)

    @async_wrap
    def map_key_set(self, *args) -> typing.List[ValueType]:
        map_hz = self.__getMapHazelcast()
        return map_hz.key_set(*args)

    @async_wrap
    def map_get_all(self, *args) -> typing.Dict[KeyType, ValueType]:
        map_hz = self.__getMapHazelcast()
        return map_hz.get_all(*args)

    def hazelcast_conf (self):
        cluster_members = self.__getServices()
        conf = list((self.__getServices(cluster_members, 'hazelcast')).values())
        return conf

def main():
    srv = Server()
    app = web.Application()
    app.add_routes(srv.routes)
    web.run_app(app=app, port=8080)


if __name__ == '__main__':
    main()
