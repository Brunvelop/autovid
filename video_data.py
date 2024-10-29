import json
from typing import List, Dict, Optional, Literal
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class VideoProductionStatus:
    text_completed: bool = False
    text_evaluation: Optional[Dict[str, any]] = None
    storyboard_completed: bool = False
    images_generated: List[bool] = field(default_factory=list)
    images_completed: List[bool] = field(default_factory=list)
    tts_completed: bool = False
    ready_to_upload: bool = False
    assets_path: Optional[Path] = None

@dataclass
class VideoYoutubeDetails:
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = field(default_factory=list)
    thumbnail_str: Optional[str] = None
    thumbnail_path: Optional[Path] = None
    uploaded: bool = False
    url: Optional[str] = None
    realse_date: Optional[str] = None
    video_type: Optional[Literal["long", "short"]] = None

@dataclass
class VideoMetadata():
    metadata_path: Optional[Path] = None
    video_path: Optional[Path] = None
    youtube_details: Optional[VideoYoutubeDetails] = VideoYoutubeDetails()
    production_status: Optional[VideoProductionStatus] = VideoProductionStatus()

    @classmethod
    def get(cls, metadata_path: Path) -> 'VideoMetadata':
        if not metadata_path.exists():
            return VideoMetadata(status_path=metadata_path)

        data = json.loads(metadata_path.read_text())
        production_status = VideoProductionStatus(
            images_completed=data.get('production_status', {}).get('images_completed', []),
            text_evaluation=data.get('production_status', {}).get('text_evaluation'),
            completed=data.get('production_status', {}).get('completed', False)
        )
        return cls(
            status_path=metadata_path,
            video_path=Path(data.get('video_path')) if data.get('video_path') else None,
            uploaded=data.get('uploaded', False),
            url=data.get('url'),
            realse_date=data.get('realse_date'),
            production_status=production_status
        )

    def save(self, metadata_path: Optional[Path] = None) -> None:
        save_path = metadata_path or self.status_path
        if not save_path:
            raise ValueError("No metadata_path provided for save")
            
        data = {
            'video_path': str(self.video_path) if self.video_path else None,
            'uploaded': self.uploaded,
            'url': self.url,
            'realse_date': self.realse_date,
            'production_status': {
                'images_completed': self.production_status.images_completed,
                'text_evaluation': self.production_status.text_evaluation,
                'completed': self.production_status.completed
            } if self.production_status else None
        }
        save_path.write_text(json.dumps(data, indent=4))
        self.metadata_path = save_path

    def update(
            self, 
            video_path: Optional[Path] = None,
            uploaded: bool = None,
            url: Optional[str] = None,
            realse_date: Optional[str] = None,
            images_completed: List[bool] = None,
            text_evaluation: Dict[str, any] = None,
            completed: bool = None
        ) -> None:
        if video_path is not None:
            self.video_path = video_path
        if uploaded is not None:
            self.uploaded = uploaded
        if url is not None:
            self.url = url
        if realse_date is not None:
            self.realse_date = realse_date
            
        if any([images_completed is not None, 
                text_evaluation is not None, 
                completed is not None]):
            if self.production_status is None:
                self.production_status = VideoProductionStatus()
            
            if images_completed is not None:
                self.production_status.images_completed = images_completed
            if text_evaluation is not None:
                self.production_status.text_evaluation = text_evaluation
            if completed is not None:
                self.production_status.completed = completed

    def sync(self) -> None:
        # Implementar lógica de sincronización si es necesaria
        pass