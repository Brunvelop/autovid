from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field

from data_types import SerieData

@dataclass
class GlobalStatus:
    series: list[SerieData] = field(default_factory=list)

class ProductionStatusManager:
    @classmethod
    def get_video_status(cls, video_assets_path: Path):
        pass

    @classmethod
    def get_global_status(cls, channel_path: Path = Path('data/MITO_TV')) -> GlobalStatus:
        return None

    @staticmethod
    def update_image_status():
        pass

if __name__ == "__main__":
    pass