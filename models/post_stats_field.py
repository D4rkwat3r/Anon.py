from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PostStatsField:
    count: Optional[int]
    my: bool
    max_count: Optional[int] = None
