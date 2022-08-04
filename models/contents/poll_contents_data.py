from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .poll_contents_answer import PollContentsAnswer


@dataclass_json
@dataclass
class PollContentsData:
    id: str
    answers: list[PollContentsAnswer]
