from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class Coordinates:
    latitude: float
    longitude: float
    zoom: Optional[float]
