import random
import warnings
from typing import Union, List

import torch
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import AutoPipelineForText2Image, StableDiffusion3Pipeline, FluxPipeline

from definitions import SDModels

class SD:
    def __init__(
            self,
            model_id: SDModels = SDModels.FAKE,
            cache_dir: Path = Path('./models'),
            low_vram: bool = True,
            verbose: bool = True,
    ):
        if verbose:
            warnings.resetwarnings()
            warnings.simplefilter("default")
        else:
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
        self.model_id = model_id.value
        self.cache_dir = cache_dir
        self.verbose = verbose
        self.low_vram = low_vram
        self.pipe = self._load_pipeline()

    def _load_pipeline(self) -> None:
        if self.model_id == SDModels.FAKE.value:
            return None
        elif self.model_id == SDModels.SDXL_TURBO.value:
            return self._load_SDXL_TURBO_pipeline()
        elif self.model_id == SDModels.SD3.value:
            return self._load_SD3_pipeline()
        elif self.model_id == SDModels.FLUX1_SCHNELL.value:
            return self._load_FLUX_pipeline()

    def _load_SDXL_TURBO_pipeline(self) -> AutoPipelineForText2Image:
        pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                variant="fp16",
                cache_dir=self.cache_dir
            )
        pipe.to("cuda")
        if self.low_vram:
            pipe.enable_attention_slicing()
        return pipe
    
    def _load_SD3_pipeline(self):
        if self.low_vram:
            pipe = StableDiffusion3Pipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16,
                cache_dir=self.cache_dir,
                text_encoder_3=None,
                tokenizer_3=None
            )
            pipe.to("cuda")

        else:
            pipe = StableDiffusion3Pipeline.from_pretrained(
                self.model_id, 
                torch_dtype=torch.float16,
                cache_dir=self.cache_dir,
            )
        return pipe

    def _load_FLUX_pipeline(self):
        pipe = FluxPipeline.from_pretrained(
            self.model_id, 
            torch_dtype=torch.bfloat16,
            cache_dir=self.cache_dir,
        )
        if self.low_vram:
            pipe.vae.enable_tiling()
            pipe.vae.enable_slicing()
            pipe.enable_sequential_cpu_offload()
        
        return pipe
    
    def _get_generation_config(self, **generation_config):
        default_config = { 'height': 1280, 'width': 768 }
        
        model_specific_config = {
            SDModels.SD3.value: {
                'negative_prompt': '',
                'num_inference_steps': 28,
                'guidance_scale': 4.0
            },
            SDModels.SDXL_TURBO.value: {
                'num_inference_steps': 5,
                'guidance_scale': 0.0
            },
            SDModels.FLUX1_SCHNELL.value: {
                'num_inference_steps': 1,
                'guidance_scale': 0.0
            }
        }
        
        default_config.update(model_specific_config.get(self.model_id, {}))
        default_config.update(generation_config)
        return default_config

    def _calculate_batch_size(self):
        batch_size = 100
        if self.model_id == SDModels.SDXL_TURBO.value or self.model_id == SDModels.SD3.value:
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            batch_size = int(vram_gb/2 + 1) 
        return batch_size

    def generate_images(self, prompt: Union[str, List[str]], **kwargs) -> List[Image.Image]:
        if self.model_id == SDModels.FAKE.value:
            return self.generate_fake_image(prompt, **kwargs)
        else:
            generation_config = self._get_generation_config(**kwargs)
            if isinstance(prompt, list):
                images = []
                batch_size = self._calculate_batch_size()
                for i in range(0, len(prompt), batch_size):
                    batch_prompts = prompt[i:i + batch_size]
                    batch_images = self.pipe(prompt=batch_prompts, **generation_config).images
                    images.extend(batch_images)
            else:
                images = self.pipe(prompt=prompt, **generation_config).images
            if self.verbose:
                print('Max mem allocated (GB) while denoising:', torch.cuda.max_memory_allocated() / (1024 ** 3))
            return images


    
    def generate_fake_image(self, prompt: str, height: int = 1280, width: int = 768) -> Image.Image:
        # Crear una imagen con fondo aleatorio
        background_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        image = Image.new('RGB', (width, height), color=background_color)
        draw = ImageDraw.Draw(image)

        # Añadir el prompt como texto
        font_size = 30
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()
        text_color = (255 - background_color[0], 255 - background_color[1], 255 - background_color[2])  # Color contraste
        
        # Dividir el prompt en líneas
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

        # Dibujar el texto
        y_text = height // 2 - (len(lines) * font_size) // 2
        for line in lines:
            text_width = draw.textlength(line, font=font)
            x_text = (width - text_width) // 2
            draw.text((x_text, y_text), line, font=font, fill=text_color)
            y_text += font_size + 5

        return image
    
if __name__ == "__main__":
    sd = SD(
        model_id=SDModels.SDXL_TURBO,
        cache_dir=Path('./models'),
        low_vram=True,
        verbose=True,
    )
    
    prompt = [
        "Un gato astronauta flotando en el espacio",
        "Un perro astronauta flotando en el espacio",
        "Un uron astronauta flotando en el espacio",
        "Un araña astronauta flotando en el espacio",
        "Un dragon astronauta flotando en el espacio",
        "Un mosca astronauta flotando en el espacio",
        "Un girafa astronauta flotando en el espacio",
        "Un caballo astronauta flotando en el espacio",
    ]
    output_path = Path("./")
    
    images = sd.generate_images(
        prompt=prompt,
        height=512,
        width=512,
        num_inference_steps=4,
        guidance_scale=0
    )
    for i, image in enumerate(images):
        image.save(output_path / f"{i}.png")
        print(f"Imagen generada y guardada en: {output_path}")
