from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from dataclasses_json import config
from .contents import TextContents
from .post_stats_field import PostStatsField


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Comment:
    id: str
    text_contents: list[TextContents] = field(metadata=config(field_name="contents"))
    author_id: str
    created_at: int
    updated_at: int
    is_author_hidden: bool
    post_id: str
    nesting_depth: int
    likes: PostStatsField
