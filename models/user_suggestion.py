from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .contents import ImageContents


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserSuggestion:
    id: str
    photo: Optional[ImageContents]
    name: str
