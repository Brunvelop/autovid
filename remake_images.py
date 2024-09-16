import random
from typing import Union, List
from abc import ABC, abstractmethod
import os
import shutil

import torch
from tqdm import tqdm
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from diffusers import AutoPipelineForText2Image, FluxPipeline

from definitions import ImageGenerators, ImageGeneratorConfig

def process_selected_images(indices, tmp_dir, output_dir):
    # Asegúrate de que los directorios existan
    tmp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Obtén la lista de archivos en el directorio temporal
    tmp_files = sorted(tmp_dir.glob('*.png'))
    
    for i, index in enumerate(indices):
        if i < len(tmp_files):
            # Copia el archivo con el nuevo nombre
            new_name = f"{index}.png"
            shutil.copy2(tmp_files[i], output_dir / new_name)

if __name__ == "__main__":
    from image_generator import FluxSchell

    import time
    start_time = time.time()

    N = 1
    OUPUT_PATH = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/images')
    OUPUT_PATH_TMP = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/remake_images')
    STORYBOARD = Path(f'data/MITO_TV/SHORTS/MITOS_GRIEGOS/{N}/text/storyboard.json')

    import json
    with open(STORYBOARD, 'r', encoding='utf-8') as f:
        storyboard = json.load(f)
    
    # Selecciona los índices deseados
    selected_indices = [1, 2, 3, 4, 5,6,7,8]  # Ajusta esta lista según tus necesidades
    prompts = [storyboard[i]["image"] for i in selected_indices]
    
    image_generator = FluxSchell(
        cache_dir=Path('./models'),
        low_vram=True,
        verbose=True,
    )

    image_generator.generate_images(
        prompts=prompts,
        output_dir=OUPUT_PATH,
        height=1344,
        width=768,
        num_inference_steps=2,
        guidance_scale=0
    )

    # Procesa las imágenes seleccionadas
    process_selected_images(selected_indices, OUPUT_PATH_TMP, OUPUT_PATH)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nGenerated in: {elapsed_time:.2f} s")