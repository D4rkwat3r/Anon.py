from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Promo:
    type: str
    key: str
    after_post_id: str
    bonus_coins: int
