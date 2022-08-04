from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .base_contents import BaseContents
from .tags_contents_data import TagsContentsData


@dataclass_json
@dataclass
class TagsContents(BaseContents):
    data: TagsContentsData
