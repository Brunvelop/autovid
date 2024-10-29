from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field

from video_data import VideoProductionStatus

@dataclass
class GlobalStatus:
    series: Dict[str, List[VideoProductionStatus]] = field(default_factory=dict)

class ProductionStatusManager:
    @classmethod
    def get_video_status(cls, video_assets_path: Path) -> VideoProductionStatus:
        status_file = video_assets_path / 'status.json'
        status = VideoProductionStatus.get(status_file) 
        return status

    @classmethod
    def get_global_status(cls, shorts_path: Path = Path('data/MITO_TV/SHORTS')) -> GlobalStatus:
        global_status = GlobalStatus()
        for serie in Path(shorts_path).iterdir():
            if not serie.is_dir():
                continue
            global_status.series[serie.name] = {}
            for video_assets_path in sorted(serie.iterdir(), key=lambda x: int(x.name)):
                if not video_assets_path.is_dir():
                    continue
                video_status = cls.get_video_status(video_assets_path)
                global_status.series[serie.name][video_assets_path] = video_status
        return global_status

    @staticmethod
    def update_image_status(status_path: Path, image_index: Optional[int] = None, is_completed: bool = False) -> VideoProductionStatus:
        status = VideoProductionStatus.get(status_path)
        status.update_image_completion_status(image_index, is_completed)
        status.save(status_path)
        return status

if __name__ == "__main__":
    pass