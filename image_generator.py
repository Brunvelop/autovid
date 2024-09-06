import random
from typing import Union, List
from abc import ABC, abstractmethod

import torch
from tqdm import tqdm
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import AutoPipelineForText2Image, FluxPipeline

from definitions import ImageGenerators, ImageGeneratorConfig


class ImageGenerator(ABC):
    def __init__(
        self, 
        cache_dir: Path = Path('./models'),
        low_vram: bool = True,
        verbose: bool = True,
    ):
        self.cache_dir = cache_dir
        self.verbose = verbose
        self.low_vram = low_vram
        self.pipe = self._load_pipeline()

    @abstractmethod
    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> List[Image.Image]:
        pass

    @abstractmethod
    def _load_pipeline(self) -> AutoPipelineForText2Image:
        pass

class FluxSchell(ImageGenerator):
    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGeneratorConfig.FLUX1_SCHNELL.value.copy()
        generation_config.update(**kwargs)

        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        BATCH_SIZE = 10
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
        generation_config = ImageGeneratorConfig.SDXL_TURBO.value.copy()
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
                ImageGenerators.SDXL_TURBO.value,
                torch_dtype=torch.float16,
                variant="fp16",
                cache_dir=self.cache_dir
            )
        pipe.to("cuda")
        if self.low_vram:
            pipe.enable_attention_slicing()
        return pipe

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

    SHORT_N = 1
    IMAGE_STYLE = " 3d animation digital art 4k detailed"
    SHORTS_FOLDER = Path('data/HOMERO/LA_ILIADA/CAPITULO_001/SHORTS')


    import json
    with open(SHORTS_FOLDER / f"{SHORT_N}/text/storyboard.json", 'r', encoding='utf-8') as f:
        storyboard = json.load(f)
    prompts = [scene["image"] + IMAGE_STYLE for scene in storyboard]
    
    image_generator = FluxSchell(
        cache_dir=Path('./models'),
        low_vram=True,
        verbose=True,
    )
    output_path = SHORTS_FOLDER / f"{SHORT_N}/images"
    image_generator.generate_images(
        prompts=prompts,
        output_dir=output_path,
        height=1920,
        width=1080,
        num_inference_steps=2,
        guidance_scale=0
    )


    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nGenerated in: {elapsed_time:.2f} s")