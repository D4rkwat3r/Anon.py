from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .image_contents_resource import ImageContentsResource


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ImageContentsData:
    extra_small: Optional[ImageContentsResource] = None
    small: Optional[ImageContentsResource] = None
    medium: Optional[ImageContentsResource] = None
    original: Optional[ImageContentsResource] = None
    large: Optional[ImageContentsResource] = None
    extra_large: Optional[ImageContentsResource] = None
