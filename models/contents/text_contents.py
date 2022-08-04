from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .base_contents import BaseContents
from .text_contents_data import TextContentsData


@dataclass_json
@dataclass
class TextContents(BaseContents):
    data: TextContentsData
