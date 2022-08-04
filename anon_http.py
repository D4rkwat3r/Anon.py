from httpx import AsyncClient
from httpx import Response
from json import dumps
from os import urandom
from base64 import urlsafe_b64encode as b64enc
from .utils import *

JSON_TYPES_UNION = Union[dict, list]
JSON_CONTENT_TYPE = "application/json; charset=utf-8"


class AnonHTTP(AsyncClient):
    """
    Wrapper for a default httpx Async Client designed to send requests to the api.anonym.network
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.headers = {"X-Device-Model": "Asus ASUS_Z01QD", "X-Android-App": "3.17.0.1193", "X-County-Code": "RU"}

    async def call(
            self,
            method: str,
            endpoint: str,
            body: Optional[bytes],
            params: Optional[dict],
            content_type: Optional[str] = None) -> Response:
        h = self.headers.copy()
        if endpoint == "/auth/register": h["X-Device-Id"] = b64enc(urandom(10)).decode("utf-8")
        if content_type: h["Content-Type"] = content_type
        response = await super().request(
            method,
            "https://api.anonym.network" + endpoint,
            headers=h,
            content=body,
            params=params if params is not None else {},
            timeout=None
        )
        if not response.is_success:
            try:
                exception = find_exception(response.json()["errors"][0])
                if isinstance(exception, RateLimitExceeded):
                    exception.reset = int(response.headers.get("X-Rate-Limit-Reset")) or 0
                raise exception
            except JSONDecodeError:
                raise IncorrectResponse()
        return response

    async def call_get(self,
                       endpoint: str,
                       params: Optional[dict] = None) -> Response:
        return await self.call("GET", endpoint, None, params)

    async def call_delete(self, endpoint: str, params: Optional[dict]) -> Response:
        return await self.call("DELETE", endpoint, None, params)

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

    async def call_patch_json(self, endpoint: str, body: JSON_TYPES_UNION) -> Response:
        return await self.call("PATCH", endpoint, dumps(body).encode("utf-8"), None, JSON_CONTENT_TYPE)
