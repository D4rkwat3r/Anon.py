from websockets import connect
from json import dumps
from json import loads
from json import JSONDecodeError
from typing import Optional
from typing import Callable
from asyncio import AbstractEventLoop
from .models import Notification
from .models import ChatMessage
from .custom_executor import CustomExecutor

EVENT_NAME_NOTIFICATION = "notification"
EVENT_NAME_ROOMS_CHANGED = "rooms-changed"
EVENT_NAME_SUBSCRIPTIONS_CHANGED = "subscriptions_changed"
EVENT_TYPE_MESSAGE_RECEIVED = "message-received"


class WebSocketListener:

    def __init__(self, rocket_id: str, rocket_token: str, mainloop: AbstractEventLoop, debug: bool = False) -> None:
        super().__init__()
        self._conn = None
        self._id = 1
        self.rocket_id = rocket_id
        self.rocket_token = rocket_token
        self.event_handlers = []
        self.close_required = False
        self.connection_id = None
        self.mainloop = mainloop
        self.debug = debug
        # "cannot schedule new futures after interpreter shutdown" python 3.9-3.10 bug fix
        self.mainloop.set_default_executor(CustomExecutor())

    async def send_json(self, data: dict) -> None:
        if data["msg"] != "connect":
            data["id"] = str(self._id)
            self._id += 1
        await self._conn.send(dumps(data))

    async def method(self, name: str, params: list):
        await self.send_json({"msg": "method", "method": name, "params": params})

    async def subscribe(self, target: str, name: str = "stream-notify-user"):
        await self.send_json({"msg": "sub", "name": name, "params": [target, False]})

    async def receive_json(self, msg: Optional[str] = None) -> Optional[dict]:
        try:
            content = loads(await self._conn.recv())
            if msg is None or content.get("msg") == msg: return content
            else: return await self.receive_json(msg)
        except JSONDecodeError: return None

    async def connect(self) -> None:
        self._conn = await connect("wss://messenger.anonym.network/websocket")
        await self.send_json({"msg": "connect", "version": "1", "support": ["1", "pre2", "pre1"]})

    async def auth(self) -> None:
        await self.method("login", [{"resume": self.rocket_token}])
        await self.method("UserPresence:online", [])
        await self.subscribe(f"{self.rocket_id}/{EVENT_NAME_NOTIFICATION}")
        await self.subscribe(f"{self.rocket_id}/{EVENT_NAME_ROOMS_CHANGED}")
        await self.subscribe(f"{self.rocket_id}/{EVENT_NAME_SUBSCRIPTIONS_CHANGED}")

    def stop(self):
        self.close_required = True

    @staticmethod
    def create_event_handler(client,
                             name: str,
                             handler: Callable,
                             payload_filter: Optional[Callable],
                             event_type: Optional[str] = None) -> dict:
        return {
            "client": client,
            "name": name,
            "event_type": event_type,
            "payload_filter": payload_filter if payload_filter is not None else lambda m: True,
            "handler": handler
        }

    def add_event_handler(self, handler: dict):
        self.event_handlers.append(handler)

    async def handle(self, data: dict):
        try: event_name = data["fields"]["eventName"].split("/")[1]
        except KeyError: return
        suitable = [handler for handler in self.event_handlers if handler["name"] == event_name]
        for handler in suitable:
            if event_name == "notification": obj = Notification.from_dict(data["fields"]["args"][0])
            elif event_name == "rooms-changed":
                if handler["event_type"] == EVENT_TYPE_MESSAGE_RECEIVED:
                    try:
                        msg_json = data["fields"]["args"][1]["lastMessage"]
                        if msg_json["u"]["_id"] == self.rocket_id: return
                        obj = ChatMessage.from_dict(msg_json)
                    except KeyError: return
                else: return
            else: return
            if handler["payload_filter"] is not None:
                if not handler["payload_filter"](obj): continue
            if self.debug: print("WS: Running callback")
            await handler["handler"](handler["client"], obj)

    async def start(self) -> None:
        if self.debug: print("WS: Starting")
        await self.connect()
        await self.auth()
        if self.debug: print("WS: Started")
        while True:
            data = await self.receive_json()
            if data is None: continue
            if self.close_required: break
            if data.get("msg") == "ping": await self.send_json({"msg": "pong"})
            else: await self.handle(data)
