from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Connection:
    likes_current_user: bool
    is_liked_by_current_user: bool
    is_bookmarked_by_current_user: bool
    blacklisted_current_user: bool
    is_blacklisted_by_current_user: bool
    chat_request_status: str
    is_in_my_subscriptions: bool
    is_subscribed_to_me: bool
