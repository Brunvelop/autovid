import os
import json
from tqdm import tqdm
from typing import Union, List

from sd import SD
from writer import Writer
from LLM import LLM
from tts import TTS
import video_editor
from definitions import LLMModels, TTSModels, SDModels, Voices, VideatorTasks, Storyboard, Scene

class VideoGenerator:
    MAX_ATTEMPTS = 2
    def __init__(
        self,
        assets_dir: str,
        llm_model: LLMModels = LLMModels.GPT4o,
        sd_model: SDModels = SDModels.SDXL_TURBO,
        tts_model: TTSModels = TTSModels.OPENAI_TTS_1,
        tts_voice: Union[Voices.Google, Voices.Azure, Voices.OpenAI] = Voices.OpenAI.NOVA,
        height: int = 1280, 
        width: int = 768, 
        style: str = None,
        low_vram: bool = True
    ):
        self.assets_dir = assets_dir
        self.audio_dir = f"{self.assets_dir}/audios"
        self.image_dir = f"{self.assets_dir}/images"
        self.script_dir = f"{self.assets_dir}/scripts"
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.script_dir, exist_ok=True)
        self.llm_model_id = llm_model
        self.sd_model_id = sd_model
        self.tts_model_id = tts_model
        self.tts_voice_id = tts_voice
        self.height = height
        self.width = width
        self.style = style
        self.low_vram = low_vram

    def _save_script(self, script: str) -> None:
        with open(f"{self.script_dir}/script.txt", "w", encoding='utf-8') as f:
            f.write(script)

    def _save_storyboard(self, storyboard: Storyboard) -> None:
        with open(f"{self.script_dir}/storyboard.json", "w", encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)

    def _load_storyboard(self) -> Storyboard:
        try:
            with open(f"{self.script_dir}/storyboard.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: storyboard.json not found.")
            return []

    def generate_storyboard(self, video_theme: str, words_number: int = 80) -> Storyboard:
        print("Generating script for video...")
        writer = Writer(LLM(model_id=self.llm_model_id))
        script = writer.generate_video_script(video_theme, words_number)
        self._save_script(script)

        print("Generating storyboard for video...")
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                storyboard = writer.generate_storyboard(script)
                break
            except Exception as e:
                if attempt < self.MAX_ATTEMPTS - 1: 
                    continue
                else:
                    raise e
        self._save_storyboard(storyboard)

        return storyboard

    def generate_audio(self) -> None:
        storyboard = self._load_storyboard()

        print("Generating audios...")
        for i , scene in tqdm(enumerate(storyboard), total=len(storyboard), desc="Generating tts"):
            TTS.generate_tts(
                text=scene.get('text'),
                output_file=f"{self.audio_dir}/{i}.mp3",
                model=self.tts_model_id,
                voice=self.tts_voice_id,
            )

    def generate_images(self) -> None:
        storyboard = self._load_storyboard()

        sd = SD(model_id=self.sd_model_id, low_vram=self.low_vram)
        print("Generating images...")
        for i, scene in tqdm(enumerate(storyboard), total=len(storyboard), desc="Generating images"):
            image = sd.generate_image(
                prompt=scene.get('image') + " " + self.style,
                output_path=f"{self.image_dir}/{i}.png",
                height=self.height,
                width=self.width,
            )
            image.save(f"{self.image_dir}/{i}.png")

    def edit_video(self, output_dir: str) -> None:
        print("Generatin video")
        video_editor.generate_video(
            images_path=self.image_dir,
            audios_path=self.audio_dir,
            output_path=output_dir
        )

    def videate(self, tasks: List[VideatorTasks], video_theme: str, output_dir: str) -> None:
        print("\n" + "=" * 50)
        print("     G E N E R A T I N G   V I D E O")
        print("=" * 50)
        print(f"Theme: {video_theme}")
        print("Tasks:")
        for task in tasks:
            print(f"  - {task.name}")
        print("=" * 50)

        if VideatorTasks.SCRIPT in tasks or VideatorTasks.FULL in tasks:
            self.generate_storyboard(video_theme)
        if VideatorTasks.AUDIO in tasks or VideatorTasks.FULL in tasks:
            self.generate_audio()
        if VideatorTasks.IMAGES in tasks or VideatorTasks.FULL in tasks:
            self.generate_images()
        if VideatorTasks.VIDEO in tasks or VideatorTasks.FULL in tasks:
            self.edit_video(output_dir)


if __name__ == "__main__":
    import time
    start_time = time.time()

    video_num = 9
    video_theme = 'La historia ficticia y humoristica estilo Animación Comedia Parodia Sátira de como un mouestro feo se transforma en guapo al estilo de el patito feo'

    vg = VideoGenerator(
        llm_model=LLMModels.GPT4o,
        tts_model=TTSModels.GOOGLE,
        tts_voice=Voices.Google.SPAIN,
        sd_model=SDModels.SDXL_TURBO,
        height=912,
        width=432,
        assets_dir=f"./tmp/{video_num}",
        style="3d animation digital art 4k detailed",
        low_vram=False
    )
    vg.videate(
        tasks=[
            # VideatorTasks.SCRIPT,
            # VideatorTasks.AUDIO,
            # VideatorTasks.IMAGES,
            # VideatorTasks.VIDEO,
            VideatorTasks.FULL
        ],
        video_theme=video_theme, 
        output_dir=f"./output/{video_num}.mp4"
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\nGenerated in: {elapsed_time:.2f} s")