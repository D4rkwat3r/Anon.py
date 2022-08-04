from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config
from dataclasses_json import LetterCase
from typing import Optional
from .user import User
from .message_counters import MessageCounters


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ChatMessage:
    id: str = field(metadata=config(field_name="_id"))
    room_id: str = field(metadata=config(field_name="rid"))
    text: str = field(metadata=config(field_name="msg"))
    sender_alias: str = field(metadata=config(field_name="alias"))
    sender: User = field(metadata=config(field_name="u"))
    server_id: int
    counters: MessageCounters
    sandstormSessionId: Optional[str] = None
    unread: Optional[bool] = None
