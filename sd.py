import random
import warnings

import torch
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import AutoPipelineForText2Image, StableDiffusion3Pipeline

from definitions import SDModels

class SD:
    def __init__(
            self,
            model_id: SDModels = SDModels.FAKE,
            cache_dir: Path = Path('./models'),
            low_vram: bool = True,
            verbose: bool = False,

    ):
        if verbose:
            warnings.resetwarnings()
            warnings.simplefilter("default")
        else:
            warnings.filterwarnings("ignore", category=FutureWarning)
            warnings.filterwarnings("ignore", category=UserWarning)
        self.model_id = model_id.value
        self.cache_dir = cache_dir
        self.pipe = self._load_pipeline(model_id, low_vram)

    def _load_pipeline(self, model_id: SDModels, low_vram: bool) -> None:
        if model_id == SDModels.FAKE.value:
            return None
        elif model_id == SDModels.SDXL_TURBO:
            return self._load_SDXL_TURBO_pipeline(low_vram)
        elif model_id == SDModels.SD3:
            return self._load_SD3_pipeline(low_vram)

    def _load_SDXL_TURBO_pipeline(self, low_vram: bool) -> AutoPipelineForText2Image:
        pipe = AutoPipelineForText2Image.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16,
                variant="fp16",
                cache_dir=self.cache_dir
            )
        pipe.to("cuda")
        if low_vram:
            pipe.enable_attention_slicing()
        return pipe
    
    def _load_SD3_pipeline(self, low_vram):
        if low_vram:
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

    def generate_image(self, prompt: str, output_path: Path, **kwargs) -> Image.Image:
        if self.model_id == SDModels.FAKE.value:
            return self.generate_fake_image(prompt, output_path, **kwargs)
        elif self.model_id == SDModels.SDXL_TURBO.value:
            return self.SDXL_TURBO_generate_image(prompt=prompt, output_path=output_path, **kwargs)
        elif self.model_id == SDModels.SD3.value:
            return self.SD3_generate_image(prompt=prompt, output_path=output_path, **kwargs)

    def SDXL_TURBO_generate_image(self, prompt: str, output_path: Path, height: int = 1280, width: int = 768, steps: int = 5, guidance_scale: float = 0.0) -> Image.Image:
        image = self.pipe(
            prompt=prompt,
            num_inference_steps=steps,
            height=height,
            width=width,
            guidance_scale=guidance_scale
        ).images[0]
        image.save(output_path)
        return image
    
    def SD3_generate_image(self, prompt: str, output_path: Path, height: int = 1280, width: int = 768, steps: int = 28, guidance_scale: float = 4.0) -> Image.Image:
        image = self.pipe(
            prompt=prompt,
            negative_prompt='',
            num_inference_steps=steps,
            height=height,
            width=width,
            guidance_scale=guidance_scale
        ).images[0]
        image.save(output_path)
        return image
    
    def generate_fake_image(self, prompt: str, output_path: Path, height: int = 1280, width: int = 768, steps: int = 15, guidance_scale: float = 0.0) -> Image.Image:
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

        # Guardar y retornar la imagen
        image.save(output_path)
        return image
    
if __name__ == "__main__":
    sd = SD(
        model_id=SDModels.SDXL_TURBO,
        cache_dir=Path('./models'),
        low_vram=True,
        verbose=False,
    )
    
    prompt = "Un gato astronauta flotando en el espacio"
    output_path = Path("./gato_astronauta.png")
    
    generated_image = sd.generate_image(
        prompt=prompt,
        output_path=output_path,
        height=512,
        width=512,
        steps=5,
        guidance_scale=0.5
    )
    
    print(f"Imagen generada y guardada en: {output_path}")
