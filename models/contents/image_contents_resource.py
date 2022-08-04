from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .image_contents_size import ImageContentsSize


@dataclass_json
@dataclass
class ImageContentsResource:
    url: str
    size: ImageContentsSize
