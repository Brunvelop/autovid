import os
import json
from tqdm import tqdm
from typing import Union

from sd import SD
from LLM import LLM
from tts import TTS
import video_editor
from definitions import LLMModels, TTSModels, SDModels, Voices, VideatorTasks

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
        style: str = None
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

    def save_script(self, script):
        with open(f"{self.script_dir}/script.txt", "w", encoding='utf-8') as f:
            f.write(script)

    def save_storyboard(self, storyboard):
        # Guardar la versión completa del storyboard
        with open(f"{self.script_dir}/storyboard.json", "w", encoding='utf-8') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        
        # Guardar los elementos individuales del storyboard
        for i, item in enumerate(storyboard):
            with open(f"{self.script_dir}/storyboard{str(i).zfill(3)}.txt", "w", encoding='utf-8') as f:
                json.dump(item, f, ensure_ascii=False, indent=2)

    def load_storyboard(self):
        try:
            with open(f"{self.script_dir}/storyboard.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Error: storyboard.json not found.")
            return []

    def generate_storyboard(self, video_theme, words_number=80):
        print("Generating script for video...")
        llm = LLM(model_id=self.llm_model_id)
        script = llm.generate_video_script(video_theme, words_number)
        self.save_script(script)

        print("Generating storyboard for video...")
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                storyboard = llm.generate_storyboard(script)
                break
            except Exception as e:
                if attempt < self.MAX_ATTEMPTS - 1: 
                    continue
                else:
                    raise e
        self.save_storyboard(storyboard)

        return storyboard

    def generate_audio(self):
        storyboard = self.load_storyboard()

        print("Generating audios...")
        for i , scene in tqdm(enumerate(storyboard), total=len(storyboard), desc="Generating tts"):
            TTS.generate_tts(
                text=scene.get('text'),
                output_file=f"{self.audio_dir}/{i}.mp3",
                model=self.tts_model_id,
                voice=self.tts_voice_id,
            )

    def generate_images(self):
        storyboard = self.load_storyboard()

        sd = SD(model_id=self.sd_model_id)
        print("Generating images...")
        for i, scene in tqdm(enumerate(storyboard), total=len(storyboard), desc="Generating images"):
            image = sd.generate_image(
                prompt=scene.get('image') + " " + self.style,
                output_path=f"{self.image_dir}/{i}.png",
                height=self.height,
                width=self.width,
            )
            image.save(f"{self.image_dir}/{i}.png")

    def edit_video(self, output_dir):
        print("Generatin video")
        video_editor.generate_video(
            images_path=self.image_dir,
            audios_path=self.audio_dir,
            output_path=output_dir
        )

    def generate_video(self, tasks, video_theme, output_dir):
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


video_num = 1
video_theme = 'Reflexion sobre el amor'

vg = VideoGenerator(
    llm_model=LLMModels.GPT4o,
    tts_model=TTSModels.GOOGLE,
    tts_voice=Voices.Google.SPAIN,
    sd_model=SDModels.SDXL_TURBO,
    height=1344,
    width=768,
    assets_dir=f"./tmp/{video_num}",
    style="old painting"
)
vg.generate_video(
    tasks=[
        # VideatorTasks.SCRIPT,
        # VideatorTasks.AUDIO,
        VideatorTasks.IMAGES,
        # VideatorTasks.VIDEO,
        # VideatorTasks.FULL
    ],
    video_theme=video_theme, 
    output_dir=f"./output/{video_num}.mp4"
)