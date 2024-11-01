from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field

from data_types import SerieData

@dataclass
class GlobalStatus:
    series: list[SerieData] = field(default_factory=list)

class ProductionStatusManager:
    @classmethod
    def get_video_data(cls, video_assets_path: Path):
        pass

    @classmethod
    def get_series_data(cls, channel_path: Path = Path('data/MITO_TV')) -> list[SerieData]:
        series = []
        if not channel_path.exists():
            return series

        for serie_dir in channel_path.iterdir():
            if not serie_dir.is_dir():
                continue
                
            serie_data = serie_dir / 'data.json'
            if not serie_data.exists():
                continue
    
            serie_data = SerieData.get(serie_data)
            series.append(serie_data)
            
        return series

    @staticmethod
    def update_image_status():
        pass

if __name__ == "__main__":
    pass