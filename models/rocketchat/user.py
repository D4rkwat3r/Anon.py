from dataclasses import dataclass
from dataclasses import field
from dataclasses_json import dataclass_json
from dataclasses_json import config
from .anon_fields import AnonFields


@dataclass_json
@dataclass
class User:
    id: str = field(metadata=config(field_name="_id"))
    username: str
    nickname: str = field(metadata=config(field_name="name"))
    anon_fields: AnonFields = field(metadata=config(field_name="customFields"))
