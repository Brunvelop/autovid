import os
import random
from dotenv import load_dotenv
from typing import Union, List
from abc import ABC, abstractmethod

import torch
import replicate
from tqdm import tqdm
from pathlib import Path
from gradio_client import Client
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

class HuggingFaceGradioFluxDev(ImageGenerator):
    def __init__(self, verbose: bool = True):
        load_dotenv()
        self.client = Client(
            src="brunvelop/FLUX.1-dev",
            hf_token=os.getenv('HUGGINGFACE_API_KEY'),
        )
        self.verbose = verbose

    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGeneratorConfig.FLUX1_SCHNELL.value.copy()
        generation_config.update(**kwargs)

        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        for i, prompt in enumerate(tqdm(prompts, desc=f"Generating {len(prompts)} images")):
            result = self._query(prompt, **generation_config)
            image_path_gradio_tmp = result[0]
            # Copy the generated image to the output directory
            image_path = output_dir / f"{i}.png"
            Image.open(image_path_gradio_tmp).save(image_path)

            if self.verbose:
                print(f"Image saved: {image_path}")
        
        if self.verbose:
            print(f"All images generated and saved in: {output_dir}")

    def _query(self, prompt: str, **kwargs):
        result = self.client.predict(
            prompt=prompt,
            seed=kwargs.get('seed', 0),
            randomize_seed=kwargs.get('randomize_seed', True),
            width=kwargs.get('width', 1024),
            height=kwargs.get('height', 1024),
            guidance_scale=kwargs.get('guidance_scale', 3.5),
            num_inference_steps=kwargs.get('num_inference_steps', 28),
            api_name="/infer"
        )
        return result

    def _load_pipeline(self) -> None:
        pass

class ReplicateFluxDev(ImageGenerator):
    def __init__(self, verbose: bool = True):
        load_dotenv()
        self.api_token = os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        self.verbose = verbose

    def generate_images(self, prompts: Union[str, List[str]], output_dir: Path, **kwargs) -> None:
        generation_config = ImageGeneratorConfig.FLUX1_SCHNELL.value.copy()
        generation_config.update(**kwargs)

        if isinstance(output_dir, Path) and output_dir.suffix == ".png":
            # Si output_dir es un archivo .png, usarlo como nombre base
            output_file = output_dir
            output_dir = output_dir.parent
        else:
            # Si output_dir es un directorio, generar nombres de archivo automáticamente
            output_file = None
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if isinstance(prompts, str):
            prompts = [prompts]
        
        for i, prompt in enumerate(tqdm(prompts, desc=f"Generating {len(prompts)} images")):
            result = self._query(prompt, **generation_config)
            
            # Download and save the image
            image_url = result[0]
            if output_file:
                # Usar el nombre de archivo especificado
                if len(prompts) > 1:
                    # Agregar un sufijo _001, _002, etc. si hay varios prompts
                    image_path = output_dir / f"{output_file.stem}_{i+1:03d}{output_file.suffix}"
                else:
                    image_path = output_file
            else:
                # Generar nombres de archivo automáticamente
                image_path = output_dir / f"{i}.png"
            self._download_image(image_url, image_path)

            if self.verbose:
                print(f"Image saved: {image_path}")
        
        if self.verbose:
            print(f"All images generated and saved in: {output_dir}")

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

    def _download_image(self, url: str, save_path: Path):
        import requests
        response = requests.get(url)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)

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
    # import time
    # import json
    # start_time = time.time()

    # # Crear el generador de imágenes una sola vez
    # image_generator = FluxSchell(
    #     cache_dir=Path('./models'),
    #     low_vram=True,
    #     verbose=True,
    # )

    # for N in range(11, 101):
    #     OUTPUT_PATH = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/images')
    #     STORYBOARD = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/text/storyboard.json')

    #     try:
    #         with open(STORYBOARD, 'r', encoding='utf-8') as f:
    #             storyboard = json.load(f)
    #         prompts = [scene["image"] for scene in storyboard]
            
    #         image_generator.generate_images(
    #             prompts=prompts,
    #             output_dir=OUTPUT_PATH,
    #             height=1344,
    #             width=768,
    #             num_inference_steps=2,
    #             guidance_scale=0
    #         )

    #         print(f"Generated images for MITOS_GRIEGOS/{N}")
    #     except Exception as e:
    #         print(f"Error processing MITOS_GRIEGOS/{N}: {str(e)}")

    # end_time = time.time()
    # elapsed_time = end_time - start_time
    # print(f"\nTotal generation time: {elapsed_time:.2f} s")

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
