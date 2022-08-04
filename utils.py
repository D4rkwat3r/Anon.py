from .exceptions import *
from json import JSONDecodeError
from typing import Union
from typing import Optional

exception_codes = {
    "FLOOD": RateLimitExceeded
}


def find_exception(data: dict) -> AnonException:
    if data["code"] in exception_codes:
        return exception_codes[data["code"]](data["code"], data["message"])
    else:
        return AnonException(data["code"], data["message"])


def deserialize(obj: object, json: Union[str, dict]) -> Optional[object]:
    if isinstance(json, str):
        try: return obj.from_json(json)
        except JSONDecodeError: raise IncorrectResponse()
    elif isinstance(json, dict):
        try: return obj.from_dict(json)
        except JSONDecodeError: raise IncorrectResponse()
    else: return None
