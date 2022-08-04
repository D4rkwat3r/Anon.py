from dataclasses import field
from dataclasses_json import config
from typing import Optional
from .coordinates import Coordinates
from .comment_write_permissions import CommentWritePermissions
from .user import User
from .post_stats import PostStats
from .contents import *


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Post:
    id: str
    is_created_by_page: Optional[bool]
    video_element_id: Optional[str]
    status: str
    type: str
    coordinates: Optional[Coordinates]
    is_commentable: bool
    has_adult_content: bool
    is_author_hidden: bool
    is_hidden_in_profile: bool
    language: str
    # awards ?
    created_at: int
    updated_at: int
    is_secret: bool
    author: Optional[User]
    stats: PostStats
    is_my_favorite: bool
    _contents: list[dict] = field(metadata=config(encoder=lambda v: v, decoder=lambda v: v))
    comment_write_permissions: Optional[CommentWritePermissions] = None

    @property
    def text_contents(self) -> list[TextContents]: return decode_text_contents(self._contents)

    @property
    def image_contents(self) -> list[ImageContents]: return decode_image_contents(self._contents)

    @property
    def tags_contents(self) -> list[TagsContents]: return decode_tags_contents(self._contents)

    @property
    def audio_contents(self) -> list[AudioContents]: return decode_audio_contents(self._contents)

    @property
    def poll_contents(self) -> list[PollContents]: return decode_poll_contents(self._contents)
