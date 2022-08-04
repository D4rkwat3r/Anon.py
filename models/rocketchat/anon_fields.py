from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AnonFields:
    anonym_id: str
    photo_url: str
    registered_at: int
