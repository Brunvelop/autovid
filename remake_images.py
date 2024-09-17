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

def process_selected_images(n, indices, base_path):
    tmp_dir = base_path / f'{n}/remake_images'
    output_dir = base_path / f'{n}/images'
    
    tmp_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tmp_files = sorted(tmp_dir.glob('*.png'))
    
    for i, index in enumerate(indices):
        if i < len(tmp_files):
            new_name = f"{index}.png"
            shutil.copy2(tmp_files[i], output_dir / new_name)

if __name__ == "__main__":
    import time
    import json
    from image_generator import FluxSchell

    start_time = time.time()

    BASE_PATH = Path('data/MITO_TV/SHORTS/MITOS_GRIEGOS')
    
    # Lista de n y sus índices correspondientes
    n_and_indices = {
        # 1: [0, 2],
        2: [1, 7, 12, 15],
        3: [1, 3],
        4: [3, 5, 6, 10],
        5: [8],
        6: [0, 2, 7, 8],
        7: [3, 4, 10],
        8: [1, 2, 9],
        9: [2, 4, 5, 7, 8, 9],
        10: [5,8, 9, 10, 11, 12]
    }

    image_generator = FluxSchell(
        cache_dir=Path('./models'),
        low_vram=True,
        verbose=True,
    )

    for n, selected_indices in n_and_indices.items():
        STORYBOARD = BASE_PATH / f'{n}/text/storyboard.json'
        
        with open(STORYBOARD, 'r', encoding='utf-8') as f:
            storyboard = json.load(f)
        
        prompts = [storyboard[i]["image"] for i in selected_indices]
        
        image_generator.generate_images(
            prompts=prompts,
            output_dir=BASE_PATH / f'{n}/remake_images',
            height=1344,
            width=768,
            num_inference_steps=2,
            guidance_scale=0
        )

        # Procesa las imágenes seleccionadas
        process_selected_images(n, selected_indices, BASE_PATH)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nAll images generated and processed in: {elapsed_time:.2f} s")