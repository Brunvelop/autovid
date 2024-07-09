from tqdm import tqdm
import os
import json

from sd import SD
import gpt
from tts import TTS
import video_editor
import definitions

class VideoGenerator:
    MAX_ATTEMPTS = 2
    TASK_SCRIPT = "script"
    TASK_AUDIO = "audio"
    TASK_IMAGES = "images"
    TASK_VIDEO = "video"
    TASK_FULL = "full"

    def __init__(self, assets_dir, style="old painting"):
        self.assets_dir = assets_dir
        self.audio_dir = f"{self.assets_dir}/audios"
        self.image_dir = f"{self.assets_dir}/images"
        self.script_dir = f"{self.assets_dir}/scripts"
        self.style = style
        os.makedirs(self.assets_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.script_dir, exist_ok=True)

    def save_script_and_images(self, script, script_and_images):
        with open(f"{self.script_dir}/script.txt", "w", encoding='utf-8') as f:
            f.write(script)
        for i, item in enumerate(script_and_images):
            with open(f"{self.script_dir}/script_and_images_{str(i).zfill(3)}.txt", "w", encoding='utf-8') as f:
                json.dump(item, f, ensure_ascii=False)

    def load_scripts(self):
        scripts_and_images = []
        i = 0
        while True:
            try:
                with open(f"{self.script_dir}/script_and_images_{str(i).zfill(3)}.txt", "r", encoding='utf-8') as f:
                    item = json.load(f)
                    scripts_and_images.append(item)
                i += 1
            except FileNotFoundError:
                break
        return scripts_and_images

    def generate_script(self, video_theme):
        print(f"Generating script for video {self.script_dir}...")
        script = gpt.generate_video_script(video_theme)
        print(script)

        print(f"Generating script and images for video {self.script_dir}...")
        for attempt in range(self.MAX_ATTEMPTS):
            try:
                script_and_images = gpt.generate_images_description_and_split_text(script)
                break
            except Exception as e:
                if attempt < self.MAX_ATTEMPTS - 1: 
                    continue
                else:
                    raise e

        self.save_script_and_images(script, script_and_images)

    def generate_audio(self):
        script_and_images = self.load_scripts()

        print("Generating audios...")
        for i, sentence in tqdm(enumerate(script_and_images), total=len(script_and_images), desc="Generating gtts"):
            TTS.generate_tts(
                model=definitions.TTSModels.GOOGLE,
                text=sentence.get('text'),
                output_file=f"{self.audio_dir}/{i}.mp3"
            )

    def generate_images(self):
        script_and_images = self.load_scripts()

        sd = SD(model_id=definitions.SDModels.FAKE)
        print("Generating images...")
        for i, sentence in tqdm(enumerate(script_and_images), total=len(script_and_images), desc="Generating images"):
            image = sd.generate_image(
                prompt=sentence.get('image') + " " + self.style,
                output_path=f"{self.image_dir}/{i}.png",
                height=1280,
                width=720,
                guidance_scale=0,
                steps=0
            )
            image.save(f"{self.image_dir}/{i}.png")

    def generate_final_video(self, output_dir):
        video_editor.generate_video(
            images_path=self.image_dir,
            audios_path=self.audio_dir,
            output_path=output_dir
        )

    def generate_video(self, tasks, video_theme, output_dir):
        if definitions.VideatorTasks.SCRIPT in tasks or definitions.VideatorTasks.FULL in tasks:
            self.generate_script(video_theme)
        if definitions.VideatorTasks.AUDIO in tasks or definitions.VideatorTasks.FULL in tasks:
            self.generate_audio()
        if definitions.VideatorTasks.IMAGES in tasks or definitions.VideatorTasks.FULL in tasks:
            self.generate_images()
        if definitions.VideatorTasks.VIDEO in tasks or definitions.VideatorTasks.FULL in tasks:
            self.generate_final_video(output_dir)


video_num = 1
video_theme = 'Reflexion sobre el amor'
vg = VideoGenerator(assets_dir=f"./tmp/{video_num}", style="old painting")
vg.generate_video(
    tasks=[
        # definitions.VideatorTasks.SCRIPT,
        # definitions.VideatorTasks.AUDIO,
        # definitions.VideatorTasks.IMAGES,
        # definitions.VideatorTasks.VIDEO,
        definitions.VideatorTasks.FULL
    ],
    video_theme=video_theme, 
    output_dir=f"./output/{video_num}.mp4"
)