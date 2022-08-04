from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class UserStatistics:
    likes: int
    thanks: int
    unique_name: bool
    thanks_next_level: int
    unseen_likes: Optional[int] = None
    feed_items_count: Optional[int] = None
    chat_request_count: Optional[int] = None
    subscribers_count: Optional[int] = None
    subscriptions_count: Optional[int] = None
