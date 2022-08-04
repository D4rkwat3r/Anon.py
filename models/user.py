from dataclasses import dataclass
from dataclasses_json import dataclass_json
from dataclasses_json import LetterCase
from typing import Optional
from .contents.image_contents import ImageContents
from .auth_info import AuthInfo
from .user_statistics import UserStatistics
from .connection import Connection


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class User:
    id: str
    url: Optional[str]
    name: str
    banner: Optional[ImageContents]
    photo: Optional[ImageContents]
    gender: str
    is_hidden: bool
    is_blocked: bool
    allow_new_subscribers: bool
    show_subscriptions: bool
    show_subscribers: bool
    is_messaging_allowed: bool
    auth: AuthInfo
    statistics: UserStatistics
    connection: Optional[Connection] = None
    tagline: Optional[str] = None
