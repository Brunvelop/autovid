import os
import io
import base64
import random
import requests
from enum import Enum
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import Union, List, Optional

import torch
import replicate
from tqdm import tqdm
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import AutoPipelineForText2Image, FluxPipeline

class ImageGenerators():
    class Local(Enum):
        FAKE = 'FAKE'
        SDXL_TURBO = {
            'name': 'stabilityai/sdxl-turbo',
            'config': {
                'num_inference_steps': 5,
                'guidance_scale': 0.0,
            }
        }
        FLUX1_SCHNELL = {
            'name': 'black-forest-labs/FLUX.1-schnell',
            'config': {
                'height': 1280,
                'width': 768,
                'num_inference_steps': 1,
                'guidance_scale': 0.0
            }
        }
    class Replicate(Enum):
        FLUX1_SCHNELL = {
            'name': 'black-forest-labs/FLUX.1-schnell',
            'config': {
                'height': 1280,
                'width': 768,
                'num_inference_steps': 1,
                'guidance_scale': 0.0
            }
        }

class ImageGenerator(ABC):
    def __new__(cls, generator: ImageGenerators, generator_config: dict = None):
        if cls is ImageGenerator:
            if generator == ImageGenerators.Local.FLUX1_SCHNELL:
                return super().__new__(FluxSchell)
            if generator == ImageGenerators.Local.SDXL_TURBO:
                return super().__new__(SDXLTURBO)
            if generator == ImageGenerators.Replicate.FLUX1_SCHNELL:
                return super().__new__(ReplicateFluxDev)
            
            if generator == ImageGenerators.SDXL:
                return super().__new__(SDXLTURBO)
            if generator == ImageGenerators.INFRA:
                return super().__new__(InfraFluxDev)
            if generator == ImageGenerators.FAKE:
                return super().__new__(FakeImageGenerator)
            raise ValueError(f"Unsupported generator: {generator}")
        return super().__new__(cls)

    def __init__(self, generator: ImageGenerators, generator_config: dict = None):
        self.generator = generator
        self.generator_config = generator_config or {}
        self.cache_dir = Path("models")
        self.pipe = self._load_pipeline()

    @abstractmethod
    def generate_images(
        self,
        prompts: Union[str, List[str]], 
        output_dir: Path,
        **kwargs
    ) -> Optional[List[Image.Image]]:
        pass

    @abstractmethod
    def _load_pipeline(self):
        pass

class FluxSchell(ImageGenerator):
    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGeneratorConfig.FLUX1_SCHNELL.value.copy()
        generation_config.update(**kwargs)

        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        BATCH_SIZE = 20
        for i in tqdm(range(0, len(prompts), BATCH_SIZE), desc=f"Generating {len(prompts)} images"):
            batch_prompts = prompts[i:i + BATCH_SIZE]
            batch_images = self.pipe(prompt=batch_prompts, **generation_config).images
            
            for j, image in enumerate(batch_images):
                image_path = output_dir / f"{i+j}.png"
                image.save(image_path)
                if self.verbose:
                    print(f"Image saved: {image_path}")
            
            if self.verbose:
                print(f'Batch {i//BATCH_SIZE + 1} completed. Max mem allocated (GB):', 
                      torch.cuda.max_memory_allocated() / (1024 ** 3))
        
        if self.verbose:
            print(f"All images generated and saved in: {output_dir}")

    def _load_pipeline(self):
        pipe = FluxPipeline.from_pretrained(
            ImageGenerators.FLUX1_SCHNELL.value, 
            torch_dtype=torch.bfloat16,
            cache_dir=self.cache_dir,
        )
        if self.low_vram:
            pipe.vae.enable_tiling()
            pipe.vae.enable_slicing()
            pipe.enable_sequential_cpu_offload()
        
        return pipe

class SDXLTURBO(ImageGenerator):
    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGenerators.Local.SDXL_TURBO.get('config').value.copy()
        generation_config.update(**kwargs)

        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        BATCH_SIZE = int(vram_gb/2 + 1) 
        for i in tqdm(range(0, len(prompts), BATCH_SIZE), desc=f"Generating {len(prompts)} images"):
            batch_prompts = prompts[i:i + BATCH_SIZE]
            batch_images = self.pipe(prompt=batch_prompts, **generation_config).images
            
            for j, image in enumerate(batch_images):
                image_path = output_dir / f"{i+j}.png"
                image.save(image_path)
                if self.verbose:
                    print(f"Image saved: {image_path}")
            
            if self.verbose:
                print(f'Batch {i//BATCH_SIZE + 1} completed. Max mem allocated (GB):', 
                      torch.cuda.max_memory_allocated() / (1024 ** 3))
        
        if self.verbose:
            print(f"All images generated and saved in: {output_dir}")

    def _load_pipeline(self) -> AutoPipelineForText2Image:
        pipe = AutoPipelineForText2Image.from_pretrained(
                ImageGenerators.Local.SDXL_TURBO.value.get('name'),
                torch_dtype=torch.float16,
                variant="fp16",
                cache_dir=self.cache_dir
            )
        pipe.to("cuda")
        # if self.low_vram:
        #     pipe.enable_attention_slicing()
        return pipe

class ReplicateFluxDev():
    def __init__(self, verbose: bool = True):
        load_dotenv()
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        self.verbose = verbose

    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGenerators.Replicate.FLUX1_SCHNELL.value.get('config').copy()
        generation_config.update(**kwargs)

        if isinstance(output_dir, Path) and output_dir.suffix == ".png":
            output_file = output_dir
            output_dir = output_dir.parent
        else:
            output_file = None
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        for i, prompt in enumerate(tqdm(prompts, desc=f"Generating {len(prompts)} images")):
            result = self._query(prompt, **generation_config)
            image_base64 = result[0].url
            if output_file:
                if len(prompts) > 1:
                    image_path = output_dir / f"{output_file.stem}_{i+1:03d}{output_file.suffix}"
                else:
                    image_path = output_file
            else:
                image_path = output_dir / f"{i}.png"
            self._save_image(image_base64, image_path)

        #     if self.verbose:
        #         print(f"Image saved: {image_path}")
        
        # if self.verbose:
        #     print(f"All images generated and saved in: {output_dir}")

    def _query(self, prompt: str, **kwargs):
        input_data = {
            "prompt": prompt,
            "go_fast": True,
            "guidance": kwargs.get('guidance_scale', 3.5),
            "num_outputs": 1,
            "aspect_ratio": "9:16",
            "output_format": "png",
            "output_quality": 80,
            "prompt_strength": 0.8,
            "num_inference_steps": kwargs.get('num_inference_steps', 28)
        }
        
        output = replicate.run(
            "black-forest-labs/flux-dev",
            input=input_data
        )
        return output

    def _save_image_old(self, image_base64: str, save_path: Path):
        if image_base64.startswith('data:image'):
            image_base64 = image_base64.split(',', 1)[1]
        
        image_data = base64.b64decode(image_base64)
        
        with open(save_path, 'wb') as f:
            f.write(image_data)
    
    def _save_image(self, image_url: str, save_path: Path):
        response = requests.get(image_url)
        response.raise_for_status() # Raise exception for failed requests
        
        image_data = response.content
        
        with open(save_path, 'wb') as f:
            f.write(image_data)

    def _load_pipeline(self) -> None:
        pass

class InfraFluxDev(ImageGenerator):
    def __init__(self, verbose: bool = True):
        super().__init__(verbose=verbose)
        self.url = "http://ec2-107-23-131-11.compute-1.amazonaws.com/predictions"
        self.headers = {
            "Content-Type": "application/json"
        }

    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        for i, prompt in enumerate(tqdm(prompts, desc=f"Generating {len(prompts)} images")):
            response = self._query(prompt, **kwargs)
            
            if response.status_code == 200:
                response_data = response.json()
                for j, image_data in enumerate(response_data['output']):
                    image = self._process_image_data(image_data)
                    image_path = output_dir / f"{i}_{j}.png"
                    image.save(image_path)
                    if self.verbose:
                        print(f"Image saved: {image_path}")
            else:
                print(f"Error in request for prompt {i}: {response.status_code}")
                print(response.text)
        
        if self.verbose:
            print(f"All images generated and saved in: {output_dir}")

    def _query(self, prompt: str, **kwargs):
        data = {
            "input": {
                "prompt": prompt,
                "aspect_ratio": kwargs.get('aspect_ratio', "9:16"),
                "num_outputs": kwargs.get('num_outputs', 1),
                "seed": kwargs.get('seed', None),
                "output_format": "png",
                "output_quality": 80,
                "disable_safety_checker": False
            }
        }
        return requests.post(self.url, json=data, headers=self.headers)

    def _process_image_data(self, image_data: str) -> Image.Image:
        if image_data.startswith('data:'):
            image_data = image_data.split(',', 1)[1]
        image_bytes = base64.b64decode(image_data)
        return Image.open(io.BytesIO(image_bytes))

    def _load_pipeline(self) -> None:
        pass

class FakeImageGenerator(ImageGenerator):
    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        for i, prompt in enumerate(tqdm(prompts, desc="Generating fake images")):
            image = self._generate_fake_image(prompt, **kwargs)
            image_path = output_dir / f"{i}.png"
            image.save(image_path)
            if self.verbose:
                print(f"Image saved: {image_path}")
        
        if self.verbose:
            print(f"All fake images generated and saved in: {output_dir}")

    def _generate_fake_image(self, prompt: str, height: int = 1280, width: int = 768) -> Image.Image:
        # Create image with random background
        background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Add prompt as text
        font_size = 30
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        text_color = (255 - background_color[0], 255 - background_color[1], 255 - background_color[2])  # Contrast color
        
        # Split prompt into lines
        words = prompt.split()
        lines = []
        current_line = []
        for word in words:
            if draw.textlength(' '.join(current_line + [word]), font=font) < width - 20:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        # Draw text
        y_text = height // 2 - (len(lines) * font_size) // 2
        for line in lines:
            text_width = draw.textlength(line, font=font)
            x_text = (width - text_width) // 2
            draw.text((x_text, y_text), line, font=font, fill=text_color)
            y_text += font_size + 5

        return image
    
    def _load_pipeline(self) -> None:
        pass

if __name__ == "__main__":

    import time

    start_time = time.time()
    image_generator = ReplicateFluxDev(verbose=True)
    image_generator.generate_images(
        prompts=[
            "A vibrant, classical art style painting depicting the scene 'El Juicio de Paris.' In the foreground, Paris stands at the center, holding a golden apple, his expression contemplative as he faces the three goddesses. To his left, Hera stands regally, her posture commanding and eyes filled with determination. To his right, Athena, clad in armor, looks resolute and confident. In the middle, Aphrodite, draped in flowing robes, gazes at Paris with a seductive smile. The background features a lush, idyllic landscape with Mount Ida rising majestically in the distance under a clear blue sky. The bold text 'El Juicio de Paris' is elegantly inscribed in the sky, formed by delicate, wispy clouds, contrasting against the serene azure backdrop.",
            "The golden apple with the inscription 'Para la más bella' in the foreground, with a backdrop of war and chaos, intricate details, and vibrant colors.",
        ],
        output_dir=Path('./testa'),
        width=768,
        height=1344,
        guidance_scale=3.5,
        num_inference_steps=28
    )
    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
