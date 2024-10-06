from __future__ import annotations
import json
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass, field
from writer import Writer
from LLM import Claude35Sonnet

@dataclass
class VideoStatus:
    images_completed: List[bool] = field(default_factory=list)
    text_evaluation: Optional[Dict[str, any]] = None
    completed: bool = False

    @classmethod
    def get(cls, status_path: Path, writer: Optional[Writer] = None) -> VideoStatus:
        if status_path.exists():
            with status_path.open('r') as f:
                data = json.load(f)
            
            # Handle case where status exists but is from an older version with text_progress
            if 'text_progress' in data:
                if writer:
                    text_path = status_path.parent / "text" / "text.txt"
                    if text_path.exists():
                        with text_path.open('r', encoding='utf-8') as f:
                            text = f.read()
                        data['text_evaluation'] = writer.evaluate_text(text)
                    else:
                        data['text_evaluation'] = None
                else:
                    data['text_evaluation'] = None
                del data['text_progress']
            
            # Handle case where status exists but is from an older version without text_evaluation
            if 'text_evaluation' not in data:
                data['text_evaluation'] = None

            status = cls(**data)
            
            # Ensure images_completed is a list
            if not isinstance(status.images_completed, list):
                status.images_completed = []
            
            # Update status based on actual image files
            images_path = status_path.parent / 'images'
            if images_path.exists() and images_path.is_dir():
                image_files = sorted(images_path.glob('*.png'))
                if len(image_files) != len(status.images_completed):
                    status.images_completed = [False] * len(image_files)
            
            status.update_completion_status()
            return status
        
        return cls.initialize(status_path)

    @classmethod
    def initialize(cls, status_path: Path) -> VideoStatus:
        images_path = status_path.parent / 'images'
        if images_path.exists() and images_path.is_dir():
            image_files = sorted(images_path.glob('*.png'))
            images_completed = [False] * len(image_files)
        else:
            images_completed = []

        status = cls(images_completed=images_completed, completed=False, text_evaluation=None)
        status.save(status_path)
        return status

    def save(self, status_path: Path) -> None:
        with status_path.open('w') as f:
            json.dump(self.__dict__, f, indent=4)

    def update_image_completion_status(self, image_index: Optional[int] = None, is_completed: bool = False) -> None:
        if image_index is not None:
            if 0 <= image_index < len(self.images_completed):
                self.images_completed[image_index] = is_completed
            else:
                raise ValueError(f"Invalid image index: {image_index}")
        
        self.update_completion_status()

    def update_completion_status(self) -> None:
        self.completed = all(self.images_completed) and self.text_evaluation is not None

    def evaluate_text(self, writer: Writer, text_path: Path) -> None:
        if text_path.exists() and self.text_evaluation is None:
            with text_path.open('r', encoding='utf-8') as f:
                text = f.read()
            self.text_evaluation = writer.evaluate_text(text)
        self.update_completion_status()

class ProductionStatusManager:
    @staticmethod
    def _process_video(video_assets_path: Path, writer: Optional[Writer] = None) -> VideoStatus:
        status_file = video_assets_path / 'status.json'
        status = VideoStatus.get(status_file, writer)
        text_path = video_assets_path / "text" / "text.txt"
        if writer and text_path.exists() and status.text_evaluation is None:
            status.evaluate_text(writer, text_path)
        status.save(status_file)
        return status

    @staticmethod
    def get_global_status(shorts_path: Path = Path('data/MITO_TV/SHORTS'), writer: Optional[Writer] = None) -> Dict[str, Dict[Path, VideoStatus]]:
        global_status = {}

        for category in Path(shorts_path).iterdir():
            if not category.is_dir():
                continue

            global_status[category.name] = {}
            for video_assets_path in sorted(category.iterdir(), key=lambda x: int(x.name)):
                if not video_assets_path.is_dir():
                    continue

                status = ProductionStatusManager._process_video(video_assets_path, writer)
                global_status[category.name][video_assets_path] = status

        return global_status

    @staticmethod
    def update_image_status(status_path: Path, image_index: Optional[int] = None, is_completed: bool = False) -> VideoStatus:
        status = VideoStatus.get(status_path)
        status.update_image_completion_status(image_index, is_completed)
        status.save(status_path)
        return status

if __name__ == "__main__":
    video_status = VideoStatus.get(
        Path('/home/user/Desktop/autovid/data/MITO_TV/SHORTS/MITOS_NORDICOS/2/status.json')
    )
    print(video_status)

    # Create a writer instance
    writer = Writer(
        llm=Claude35Sonnet(
            low_vram=False,
            llm_config={
                'temperature': 0.5,
            }
        )
    )

    # Get global status (including text evaluations)
    global_status = ProductionStatusManager.get_global_status(writer=writer)
    print(global_status)