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
class VideoMetadata:
    metadata_path: Optional[Path] = None
    video_path: Optional[Path] = None
    youtube_details: Optional[VideoYoutubeDetails] = VideoYoutubeDetails()
    production_status: Optional[VideoProductionStatus] = VideoProductionStatus()

    @classmethod
    def get(cls, metadata_path: Path) -> 'VideoMetadata':
        if not metadata_path.exists():
            return VideoMetadata(metadata_path=metadata_path)

        data = json.loads(metadata_path.read_text())
        
        youtube_data = data.get('youtube_details', {})
        youtube_details = VideoYoutubeDetails(
            **{k:v for k,v in youtube_data.items() if k != 'thumbnail_path'},
            thumbnail_path=Path(youtube_data.get('thumbnail_path')) if youtube_data.get('thumbnail_path') else None
        )
        
        prod_data = data.get('production_status', {})
        production_status = VideoProductionStatus(
            **{k:v for k,v in prod_data.items() if k != 'assets_path'},
            assets_path=Path(prod_data.get('assets_path')) if prod_data.get('assets_path') else None
        )

        return cls(
            metadata_path=metadata_path,
            video_path=Path(data.get('video_path')) if data.get('video_path') else None,
            youtube_details=youtube_details,
            production_status=production_status
        )


    def save(self, metadata_path: Optional[Path] = None) -> None:
        save_path = metadata_path or self.metadata_path
        if not save_path:
            raise ValueError("No metadata_path provided for save")
            
        data = {
            'video_path': str(self.video_path) if self.video_path else None,
            'youtube_details': self._serialize_dataclass(self.youtube_details),
            'production_status': self._serialize_dataclass(self.production_status)
        }

        save_path.write_text(json.dumps(data, indent=4))
        self.metadata_path = save_path


    def update(
            self,
            video_path: Optional[Path] = None,
            youtube_details: Optional[Dict] = None,
            production_status: Optional[Dict] = None
        ) -> None:
        if video_path:
            self.video_path = video_path
            
        if youtube_details:
            if not self.youtube_details:
                self.youtube_details = VideoYoutubeDetails()
                
            for key, value in youtube_details.items():
                if hasattr(self.youtube_details, key):
                    if key == 'thumbnail_path' and value:
                        setattr(self.youtube_details, key, Path(value))
                    else:
                        setattr(self.youtube_details, key, value)
                        
        if production_status:
            if not self.production_status:
                self.production_status = VideoProductionStatus()
                
            for key, value in production_status.items():
                if hasattr(self.production_status, key):
                    if key == 'assets_path' and value:
                        setattr(self.production_status, key, Path(value))
                    else:
                        setattr(self.production_status, key, value)


    def _serialize_dataclass(self, obj):
            if obj is None:
                return None
            
            data = {}
            for field_name, field_value in obj.__dict__.items():
                if isinstance(field_value, Path):
                    data[field_name] = str(field_value) if field_value else None
                else:
                    data[field_name] = field_value
            return data
    
    def sync(self) -> None:
        # Implementar lógica de sincronización si es necesaria
        pass

@dataclass
class SerieMetadata:
    metadata_path: Optional[Path] = None
    name: Optional[str] = None
    descrption: Optional[str] = None
    videos: List[VideoMetadata] = field(default_factory=list)


if __name__ == "__main__":
    # Test creating a new metadata file
    test_path = Path("test_metadata.json")
    
    # Create new metadata object
    metadata = VideoMetadata(metadata_path=test_path)
    
    # Update with test data
    metadata.update(
        video_path=Path("videos/test_video.mp4"),
        youtube_details={
            "title": "Test Video",
            "description": "This is a test video",
            "tags": ["test", "video"],
            "video_type": "long",
            "thumbnail_path": "thumbnails/test.jpg"
        },
        production_status={
            "text_completed": True,
            "storyboard_completed": True,
            "images_generated": [True, True, False],
            "images_completed": [True, False, False],
            "tts_completed": False,
            "assets_path": "assets/test/"
        }
    )
    
    # Save metadata
    metadata.save()
    
    # Load saved metadata
    loaded_metadata = VideoMetadata.get(test_path)
    
    # Print loaded data to verify
    print("\nLoaded metadata:")
    print(f"Video path: {loaded_metadata.video_path}")
    print("\nYoutube details:")
    for key, value in loaded_metadata.youtube_details.__dict__.items():
        print(f"{key}: {value}")
    print("\nProduction status:")
    for key, value in loaded_metadata.production_status.__dict__.items():
        print(f"{key}: {value}")
        
    # Clean up test file
    # test_path.unlink(missing_ok=True)
