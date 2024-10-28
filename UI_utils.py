from __future__ import annotations
import json
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class VideoStatus:
    images_completed: List[bool] = field(default_factory=list)
    text_evaluation: Optional[Dict[str, any]] = None
    completed: bool = False
    assets_path: Optional[Path] = None

    @classmethod
    def get(cls, status_path: Path) -> VideoStatus:
        if not status_path.exists():
            return cls(
                images_completed=[],
                text_evaluation=None, 
                completed=False,
                assets_path=status_path.parent
            )

        data = json.loads(status_path.read_text())
        status = cls(
            images_completed=data.get('images_completed', []),
            text_evaluation=data.get('text_evaluation'), 
            completed=data.get('completed', False),
            assets_path=status_path.parent
        )
        return status

    def save(self) -> None:
        if not self.status_path:
            raise ValueError("Cannot save status: assets_path is not set")
            
        data = {
            'images_completed': self.images_completed,
            'text_evaluation': self.text_evaluation,
            'completed': self.completed
        }
        self.status_path.write_text(json.dumps(data, indent=4))

    def update(
            self, 
            images_completed: List[bool] = None,
            text_evaluation: Dict[str, any] = None,
            completed: bool = None
        ) -> None:
        if images_completed is not None:
            self.images_completed = images_completed
        if text_evaluation is not None:
            self.text_evaluation = text_evaluation
        if completed is not None:
            self.completed = completed
        self.save()

@dataclass
class GlobalStatus:
    series: Dict[str, List[VideoStatus]] = field(default_factory=dict)

class ProductionStatusManager:
    @classmethod
    def get_video_status(cls, video_assets_path: Path) -> VideoStatus:
        status_file = video_assets_path / 'status.json'
        status = VideoStatus.get(status_file) 
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
    def update_image_status(status_path: Path, image_index: Optional[int] = None, is_completed: bool = False) -> VideoStatus:
        status = VideoStatus.get(status_path)
        status.update_image_completion_status(image_index, is_completed)
        status.save(status_path)
        return status

if __name__ == "__main__":
    pass