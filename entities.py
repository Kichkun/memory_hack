from dataclasses import dataclass
from typing import Dict, List


@dataclass
class MoscowEntity:
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
