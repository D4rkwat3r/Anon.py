from httpx import AsyncClient
from httpx import Response
from httpx import Timeout
from httpx import TimeoutException
from httpx import ConnectTimeout
from json import dumps
from .utils import *
from .exceptions import RocketException

JSON_TYPES_UNION = Union[dict, list]
JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class RocketHTTP(AsyncClient):
    """
    Wrapper for a default httpx Async Client designed to send requests to the messenger.anonym.network
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.headers = {"User-Agent": ""}

    async def call(
            self,
            method: str,
            endpoint: str,
            body: Optional[bytes],
            params: Optional[dict],
            content_type: Optional[str] = None) -> Response:
        h = self.headers.copy()
        if content_type: h["Content-Type"] = content_type
        try:
            response = await super().request(
                method,
                "https://messenger.anonym.network/api/" + endpoint,
                headers=h,
                content=body,
                params=params,
                timeout=Timeout(3, connect=3)
            )
        except (TimeoutException, ConnectTimeout):
            return await self.call(method, endpoint, body, params, content_type)
        if response.status_code != 200:
            errors = response.json()
            raise RocketException(errors["error"], errors["errorType"])
        return response

    async def call_get(self,
                       endpoint: str,
                       params: Optional[dict] = None) -> Response:
        return await self.call("GET", endpoint, None, params)

    async def call_post(self,
                        endpoint: str,
                        body: bytes) -> Response:
        return await self.call("POST", endpoint, body, None)

    async def call_post_string(self,
                               endpoint: str,
                               body: str) -> Response:
        return await self.call("POST", endpoint, body.encode("utf-8"), None)

    async def call_post_json(
            self,
            endpoint: str,
            body: JSON_TYPES_UNION) -> Response:
        return await self.call("POST", endpoint, dumps(body).encode("utf-8"), None, JSON_CONTENT_TYPE)
