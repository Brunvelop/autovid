import json
from typing import List
from pathlib import Path
from typing import List, TypedDict

class ProductionStatusManager:
    class VideoStatus(TypedDict):
        images_completed: List[bool]
        completed: bool = False

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
                if not status_file.exists():
                    ProductionStatusManager._initialize_status(status_file)
                
                status = ProductionStatusManager._get_video_status(status_file)

                global_status[category.name][video_assets_path] = status

        return global_status

    @staticmethod
    def _get_video_status(status_path: Path) -> VideoStatus:
        if status_path.exists():
            with status_path.open('r') as f:
                data = json.load(f)
        return data
    
    @staticmethod
    def _save_video_status(status: VideoStatus, status_path: Path) -> None:
        with status_path.open('w') as f:
            json.dump(status, f, indent=4)

    @staticmethod
    def _initialize_status(status_path: Path) -> VideoStatus:
        images_path = status_path.parent / 'images'
        image_files = sorted(images_path.glob('*.png'))
        images_completed = [False] * len(image_files)
        
        status: ProductionStatusManager.VideoStatus = {
            'images_completed': images_completed,
            'completed': False
        }
        
        ProductionStatusManager._save_video_status(status, status_path)
        
        return status




if __name__ == "__main__":
    global_status = ProductionStatusManager.get_global_status(Path('data/MITO_TV/SHORTS'))