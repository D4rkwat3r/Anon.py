from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config


@dataclass_json
@dataclass
class NotificationMessage:
    text: str = field(metadata=config(field_name="msg"))
