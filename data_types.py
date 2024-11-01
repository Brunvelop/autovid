from pathlib import Path
from typing import List, Dict, Optional, Literal, Union

from pydantic import BaseModel, Field

class Scene(BaseModel):
    text:  Optional[str] = None
    image:  Optional[str] = None

class Storyboard(BaseModel):
    scenes: List[Scene] = Field(default_factory=list)

    @classmethod
    def load(cls, filename: Path) -> 'Storyboard':
        if not filename.exists():
            return cls()
            
        json_data = filename.read_text(encoding='utf-8') 
        data = cls.model_validate_json(json_data)
        return data

    def save(self, filename: Path) -> None:
        filename.parent.mkdir(parents=True, exist_ok=True)
        filename.write_text(self.model_dump_json(indent=2), encoding='utf-8')

    @classmethod
    def update(cls, filename: Path, updates: 'Storyboard') -> None:
        storyboard = cls.load(filename)
        for i, update_scene in enumerate(updates.scenes):
            if i < len(storyboard.scenes):
                storyboard.scenes[i].text = update_scene.text
                storyboard.scenes[i].image = update_scene.image
        storyboard.save(filename)

class VideoProductionStatus(BaseModel):
    text_completed: bool = False
    text_evaluation: Optional[Dict[str, Union[None, float]]] = None
    storyboard_completed: bool = False
    images_generated: List[bool] = Field(default_factory=list)
    images_completed: List[bool] = Field(default_factory=list)
    tts_completed: bool = False
    ready_to_upload: bool = False
    assets_path: Optional[Path] = None

class VideoYoutubeDetails(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None 
    tags: Optional[List[str]] = Field(default_factory=list)
    thumbnail_str: Optional[str] = None
    thumbnail_path: Optional[Path] = None
    uploaded: bool = False
    url: Optional[str] = None
    realse_date: Optional[str] = None
    video_type: Optional[Literal["long", "short"]] = None

class VideoData(BaseModel):
    json_data_path: Optional[Path] = None
    video_path: Optional[Path] = None
    text: Optional[str] = None
    storyboard : Optional[Storyboard] = Field(default_factory=Storyboard)
    video_n: Optional[int] = None
    youtube_details: Optional[VideoYoutubeDetails] = Field(default_factory=VideoYoutubeDetails)
    production_status: Optional[VideoProductionStatus] = Field(default_factory=VideoProductionStatus)
    text_cost: Optional[float] = None

    @classmethod
    def get(cls, json_data_path: Path) -> 'VideoData':
        if not json_data_path.exists():
            return cls(json_data_path=json_data_path)
        
        json_data = json_data_path.read_text(encoding='utf-8')
        return cls.model_validate_json(json_data)

    def save(self, json_data_path: Optional[Path] = None) -> None:
        save_path = json_data_path or self.json_data_path
        if not save_path:
            raise ValueError("No save path provided")
            
        self.json_data_path = save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(self.model_dump_json(indent=4), encoding='utf-8')

    def sync(self) -> None:
        # Implementar lógica de sincronización si es necesaria
        pass

class SerieData(BaseModel):
    json_data_path: Optional[Path] = None
    serie_path: Optional[Path] = None
    name: Optional[str] = None
    serie_theme: Optional[str] = None
    used_themes: List[str] = Field(default_factory=list)
    expertise: Optional[str] = None
    num_stories: Optional[int] = None
    videos: List[VideoData] = Field(default_factory=list)

    @classmethod 
    def get(cls, json_data_path: Path) -> 'SerieData':
        if not json_data_path.exists():
            return cls(json_data_path=json_data_path)
        
        json_data = json_data_path.read_text(encoding='utf-8')
        serie_data = cls.model_validate_json(json_data)
        
        if not serie_data.videos:
            videos = []
            for video_dir in serie_data.serie_path.iterdir():
                if video_dir.is_dir():
                    video_json_path = video_dir / "video_data.json"
                    if video_json_path.exists():
                        videos.append(VideoData.get(video_json_path))
            serie_data.videos = sorted(videos, key=lambda video: video.video_n)
            
        return serie_data

    def save(self, json_data_path: Optional[Path] = None) -> None:
        save_path = json_data_path or self.json_data_path
        if not save_path:
            raise ValueError("No metadata path provided")
            
        self.json_data_path = save_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        for video in self.videos:
            video.save()
            
        serie_data = self.model_copy()
        serie_data.videos = []
        
        save_path.write_text(serie_data.model_dump_json(indent=4), encoding='utf-8')


if __name__ == "__main__":
    # 1. Create a test metadata path
    test_path = Path("test_metadata.json")
    
    # 2. Create a new VideoMetadata instance with some test data
    video = VideoData(
        json_data_path=test_path,
        text="This is a test video script",
        text_cost=10.5,
        youtube_details=VideoYoutubeDetails(
            title="Test Video",
            description="This is a test description",
            tags=["test", "video"],
            video_type="long"
        ),
        production_status=VideoProductionStatus(
            text_completed=True,
            storyboard_completed=False,
            images_completed=[True, False, True],
            tts_completed=True
        )
    )
    
    # 3. Save the metadata to file
    video.save()
    print("Saved video metadata to:", test_path)
    
    # 4. Load the metadata back and verify
    loaded_video = VideoData.get(test_path)
    print("\nLoaded video metadata:")
    print(f"Title: {loaded_video.youtube_details.title}")
    print(f"Text: {loaded_video.text}")
    print(f"Production status: {loaded_video.production_status.text_completed}")
    
    # 5. Test SerieMetadata
    serie = SerieData(
        serie_path=Path("test_serie"),
        name="Test Serie",
        serie_theme="Technology",
        expertise="Beginner",
        num_stories=5,
        videos=[video]
    )
    
    print("\nSerie metadata:")
    print(f"Name: {serie.name}")
    print(f"Theme: {serie.serie_theme}")
    print(f"Number of videos: {len(serie.videos)}")
