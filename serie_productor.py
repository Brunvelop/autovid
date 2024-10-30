from abc import ABC
from tqdm import tqdm
from pathlib import Path

from tools.writer import Writer
from data_types import SerieData, VideoData, VideoYoutubeDetails, VideoProductionStatus

class SerieGenerator(ABC):
    def __init__(self, writer: Writer, serie_data: SerieData):
        self.writer = writer
        self.serie_data: SerieData = serie_data

    def generate_serie_text(self) -> list[VideoData]:
        pass

class ShortsSerieGenerator(SerieGenerator):
    def generate_serie_text(self) -> SerieData:
        videos: VideoData = []
        for i in tqdm(range(self.serie_data.num_stories), desc="Generating videos"):
            video = self._generate_video_text()
            videos.append(video)

        print("\nSorting stories by score...")
        videos.sort(key=lambda x: x.production_status.text_evaluation['average_score'], reverse=True)
        
        for i, video in enumerate(videos):
            video.json_data_path = Path(f"{self.serie_data.serie_path}/{i}/video_data.json")
        
        self.serie_data.videos = videos
        self.serie_data.save()
        return self.serie_data

    def _generate_video_text(self) -> VideoData:
        total_cost = 0
        print("Generating theme for text...")
        theme_response = self.writer.generate_theme(
                expertise=self.serie_data.expertise,
                serie_theme=self.serie_data.serie_theme,
                used_themes=self.serie_data.used_themes
            )
        total_cost += theme_response['cost']
        self.serie_data.used_themes.append(theme_response['text'])
        print(f"Theme generated: {theme_response['text']}")

        print("Generating initial story...")
        story_response = self.writer.generate_story(self.serie_data.expertise, self.serie_data.serie_theme)
        total_cost += story_response['cost']
        print("Initial story generated")

        print("Improving story...")
        improved_response = self.writer.improve_story(self.serie_data.expertise, story_response['text'])
        total_cost += improved_response['cost']
        print("Story improved")

        print("Evaluating story...")
        evaluation = self.writer.evaluate_text(improved_response['text'])

        return VideoData(
            json_data_path = None,
            video_path = None,
            text = improved_response['text'],
            youtube_details = VideoYoutubeDetails(
                title = theme_response['text'],
                description = improved_response['text'],
                video_type = 'short',
            ),
            production_status = VideoProductionStatus(
                text_completed=True,
                text_evaluation=evaluation,
                assets_path= None
            ),
            text_cost=total_cost,
        )

if __name__ == "__main__":
    from generators.LLM import Models, LLM

    writer = Writer(LLM(model=Models.OpenAI.GPT4oMini))
    
    serie_data = SerieData(
        json_data_path="./data/my_serie2/data.json",
        serie_path="./data/my_serie2",
        num_stories=2,  # Will generate 5 videos
        expertise="technology",  # Topic expertise
        serie_theme="Latest AI trends and developments",
        used_themes=[]  # Empty list to start tracking used themes
    )
    
    # 3. Create shorts generator instance
    generator = ShortsSerieGenerator(writer=writer, serie_data=serie_data)
    
    # 4. Generate the series content
    result = generator.generate_serie_text()
    print(f"\nGeneration completed!")
    print(f"Generated {len(result.videos)} videos")
    print(f"Content saved to: {result.serie_path}")

