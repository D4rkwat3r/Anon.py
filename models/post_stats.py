from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from .post_stats_field import PostStatsField


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class PostStats:
    likes: PostStatsField
    views: PostStatsField
    comments: PostStatsField
    shares: PostStatsField
    replies: PostStatsField
    time_left_to_space: PostStatsField
