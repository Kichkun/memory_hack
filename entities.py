from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class MoscowEntity:
    source_url: str
    name: str
    date: str
    place_of_birth: str
    general_military_info: Dict[str, str]
    medals: List[str]
    img_path: str
    img_url: str
    side_media_urls: List[str]
    biography: Dict[str, str]
    member_of_battles: List[str]


@dataclass
class GeneralEntity:
    source_url: str
    name: str
    date: str
    photo_path: Optional[str] = None
    facial_vector: Optional[Any] = None
    meta: Optional[Dict[Any, Any]] = None
