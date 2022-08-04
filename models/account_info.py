from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccountInfo:
    id: str
    login: str
    email: Optional[str]
    rocket_key: str
    rocket_id: str
    is_disabled: bool
    level: int
    token: str
    rt_node: str
    rocket_token: str = ""
