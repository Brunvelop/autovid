import json
from typing import List
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class VideoStatus:
    images_completed: List[bool]
    completed: bool = False

    @classmethod
    def get(cls, status_path: Path) -> 'VideoStatus':
        if status_path.exists():
            with status_path.open('r') as f:
                data = json.load(f)
            return cls(**data)
        return cls.initialize(status_path)

    @classmethod
    def initialize(cls, status_path: Path) -> 'VideoStatus':
        images_path = status_path.parent / 'images'
        if not images_path.exists() or not images_path.is_dir():
            raise FileNotFoundError(f"Can't get video status, no images dir: {images_path}")

        image_files = sorted(images_path.glob('*.png'))
        images_completed = [False] * len(image_files)
        status = cls(images_completed=images_completed, completed=False)
        status.save(status_path)
        return status

    def update(self, image_index: int = None, is_completed: bool = False) -> None:
        if image_index is not None:
            if 0 <= image_index < len(self.images_completed):
                self.images_completed[image_index] = is_completed
            else:
                raise ValueError(f"Invalid image index: {image_index}")
        
        self.completed = all(self.images_completed)

    def save(self, status_path: Path) -> None:
        with status_path.open('w') as f:
            json.dump(self.__dict__, f, indent=4)

class ProductionStatusManager:
    @staticmethod
    def get_global_status(shorts_path: Path = Path('data/MITO_TV/SHORTS')):
        global_status = {}
        for category in Path(shorts_path).iterdir():
            if not category.is_dir():
                continue

            global_status[category.name] = {}
            for video_assets_path in sorted(category.iterdir(), key=lambda x: int(x.name)):
                if not video_assets_path.is_dir():
                    continue

                status_file = video_assets_path / 'status.json'
                status = VideoStatus.get(status_file)
                global_status[category.name][video_assets_path] = status

        return global_status

    @staticmethod
    def update_image_status(status_path: Path, image_index: int = None, is_completed: bool = False) -> VideoStatus:
        status = VideoStatus.get(status_path)
        status.update(image_index, is_completed)
        status.save(status_path)
        return status


if __name__ == "__main__":
    video_status = VideoStatus.get(
        status_path=Path('/home/user/Desktop/autovid/data/MITO_TV/SHORTS/MITOS_NORDICOS/2/status.json')
    )
    video_status