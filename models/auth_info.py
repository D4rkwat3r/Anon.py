from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AuthInfo:
    is_disabled: bool
    level: int
    last_seen_at: Optional[int] = None
    login: Optional[str] = None
    email: Optional[str] = None
    referral_code: Optional[str] = None
    rocket_id: Optional[str] = None
