from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from .base_contents import BaseContents
from .image_contents_data import ImageContentsData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ImageContents(BaseContents):
    id: str
    data: ImageContentsData
