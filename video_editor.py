import os
import random
import tempfile
from typing import Callable

import numpy as np
import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import cv2
import math
import numpy
from PIL import Image
from pathlib import Path

import vid_transition


import os
from pathlib import Path
import moviepy.editor as mp
from DepthFlow import DepthScene
from PIL import Image
from Broken.Externals.Depthmap import DepthAnythingV2
from DepthFlow.Motion import Presets

#VIDEO EFFECTS:
def add_positional_noise(clip: mp.VideoClip, noise_level: int = 5, inertia: float = 0.9) -> mp.VideoClip:
    last_dx = 0
    last_dy = 0

    def effect(get_frame: callable, t: float) -> np.ndarray:
        nonlocal last_dx, last_dy
        frame = get_frame(t)
        h, w = frame.shape[:2]

        # Generar desplazamiento aleatorio para las coordenadas x e y
        dx = random.randint(-noise_level, noise_level)
        dy = random.randint(-noise_level, noise_level)

        # Aplicar inercia para suavizar el cambio de desplazamiento
        dx = (inertia * last_dx) + ((1 - inertia) * dx)
        dy = (inertia * last_dy) + ((1 - inertia) * dy)

        # Actualizar los últimos valores de desplazamiento
        last_dx = dx
        last_dy = dy

        # Crear una matriz de transformación para el desplazamiento
        M = numpy.float32([[1, 0, dx], [0, 1, dy]])

        # Aplicar un desplazamiento afín a la imagen
        frame_with_noise = cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

        return frame_with_noise

    return clip.fl(effect)


def zoom_in_face_effect(clip: mp.VideoClip, zoom_ratio: float = 0.04, face_zoom: bool = True) -> mp.VideoClip:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def effect(get_frame: Callable[[float], np.ndarray], t: float) -> np.ndarray:
        frame = get_frame(t)
        img = Image.fromarray(frame)
        base_size = img.size

        if face_zoom:
            # Convertir la imagen a escala de grises para la detección de rostros
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            # Si se detectan rostros, centrar el zoom en el rostro más grande
            if len(faces) > 0:
                faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)  # Ordenar por tamaño de rostro
                x, y, w, h = faces[0]  # Tomar el rostro más grande
                center_x = x + w / 2
                center_y = y + h / 2
            else:
                center_x = base_size[0] / 2
                center_y = base_size[1] / 2
        else:
            center_x = base_size[0] / 2
            center_y = base_size[1] / 2

        # Calcular el nuevo tamaño de la imagen con el efecto de zoom
        new_width = math.ceil(base_size[0] * (1 + (zoom_ratio * t)))
        new_height = math.ceil(base_size[1] * (1 + (zoom_ratio * t)))

        # Asegurarse de que las nuevas dimensiones sean pares
        new_width += new_width % 2
        new_height += new_height % 2

        # Redimensionar la imagen
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Calcular el área de recorte centrada en el rostro o en el centro
        left = max(center_x * (1 + (zoom_ratio * t)) - base_size[0] / 2, 0)
        top = max(center_y * (1 + (zoom_ratio * t)) - base_size[1] / 2, 0)
        right = left + base_size[0]
        bottom = top + base_size[1]

        # Asegurarse de que el área de recorte no exceda las dimensiones de la imagen
        left, top, right, bottom = [int(val) for val in [left, top, right, bottom]]
        if right > new_width:
            right = new_width
            left = new_width - base_size[0]
        if bottom > new_height:
            bottom = new_height
            top = new_height - base_size[1]

        # Recortar y redimensionar la imagen al tamaño base
        img = img.crop((left, top, right, bottom)).resize(base_size, Image.LANCZOS)

        # Convertir la imagen a un array y cerrarla
        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)

def _create_or_clear_transitions_folder(transitions_folder: Path = Path('./tmp/transitions')) -> None:
    transitions_folder.mkdir(parents=True, exist_ok=True)
    for file in transitions_folder.iterdir():
        file.unlink()

def get_audio_and_duration(n: int, audios_path: Path) -> tuple[mp.AudioFileClip, float]:
    audio_file = audios_path / f"{n}.mp3"
    audio = mp.AudioFileClip(str(audio_file))
    audio = audio.set_duration(audio.duration - 0.2)
    duration = audio.duration + 0.2
    return audio, duration

def generate_transition(slide1: mp.VideoClip, slide2: mp.VideoClip, num_frames: int) -> tuple[mp.VideoFileClip, mp.VideoFileClip]:
    transitions_dir = Path('./tmp/transitions')
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=transitions_dir) as temp1, \
         tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=transitions_dir) as temp2, \
         tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir=transitions_dir) as temp_transition:

        slide1.write_videofile(str(temp1.name))
        slide2.write_videofile(str(temp2.name))

        animations = ["rotation", "rotation_inv", "zoom_in", "zoom_out", "translation", "translation_inv"]
        vid_transition.main(
            input_videos=[str(temp1.name), str(temp2.name)],
            num_frames=num_frames,
            output=str(temp_transition.name),
            animation=random.choice(animations),
            max_rotation=45,
            max_distortion=0.7,
            max_blur=0.2,
            max_brightness=1.0,
            max_zoom=2.0,
            debug=False,
            art=False,
            remove=False,
            merge=False
        )

        temp_transition_path = Path(temp_transition.name)
        transition_clip_1 = mp.VideoFileClip(str(temp_transition_path.with_name(f"{temp_transition_path.stem}_phase1.mp4")))
        transition_clip_2 = mp.VideoFileClip(str(temp_transition_path.with_name(f"{temp_transition_path.stem}_phase2.mp4")))
        print(f"Transition clips: {transition_clip_1, transition_clip_2}")

        return transition_clip_1, transition_clip_2
    
def adjust_video_duration(video: mp.VideoClip) -> mp.VideoClip:
    if video.duration >= 59:
        return video.fx(vfx.speedx, video.duration/59).set_fps(30)
    return video

def generate_video(
    fps: int = 30,
    transition_n_frames: int = 6,
    images_path: Path = Path('tmp/images'),
    audios_path: Path = Path('tmp/audios'),
    transitions_path: Path = Path('tmp/transitions'),
    output_path: Path = Path('output/video.mp4')
) -> None:
    _create_or_clear_transitions_folder(transitions_path)

    images = sorted(images_path.iterdir(), key=lambda x: int(x.stem))

    timeline = []
    for n, image in enumerate(images[:-1]):  # Excluimos la última imagen porque no tiene una imagen siguiente para la transición

        image_clip_1 = mp.ImageClip(str(image)).set_fps(30)
        audio_1, duration_1 = get_audio_and_duration(n, audios_path)
        image_clip_1 = image_clip_1.set_duration(duration_1 -  transition_n_frames / fps / 2)
        image_clip_1 = zoom_in_face_effect(image_clip_1)

        image_clip_2 = mp.ImageClip(str(images[n+1])).set_fps(30)
        audio_2, duration_2 = get_audio_and_duration(n+1, audios_path)
        image_clip_2 = image_clip_2.set_duration(duration_2 -  transition_n_frames / fps / 2)

        transition_clip_1, transition_clip_2 = generate_transition(image_clip_1, image_clip_2, transition_n_frames)
        full_video_1 = mp.concatenate_videoclips([image_clip_1, transition_clip_1, transition_clip_2]).set_audio(audio_1)
        
        timeline.append(full_video_1)

    image_clip_last = mp.ImageClip(str(images[n+1])).set_fps(30)
    audio_last, duration_last = get_audio_and_duration(n+1, audios_path)
    image_clip_last = image_clip_2.set_duration(duration_last -  transition_n_frames / fps / 2)
    image_clip_last = zoom_in_face_effect(image_clip_last)
    image_clip_last = image_clip_last.set_audio(audio_last)
    timeline.append(image_clip_last)

    # Concatenar clips y ajustar duración
    video = mp.concatenate_videoclips(timeline)
    video = adjust_video_duration(video)

    # Aplicar efecto de ruido como postprocesado
    video = add_positional_noise(video, noise_level=100, inertia=0.995)

    # Escribir archivo de video
    video.write_videofile(str(output_path))

def generate_depth_video(
    fps: int = 30,
    transition_n_frames: int = 6,
    images_path: Path = Path('tmp/images'),
    audios_path: Path = Path('tmp/audios'),
    transitions_path: Path = Path('tmp/transitions'),
    output_path: Path = Path('output/video.mp4')
) -> None:
    _create_or_clear_transitions_folder(transitions_path)

    images = sorted(images_path.iterdir(), key=lambda x: int(x.stem))

    timeline = []
    for n, image_path in enumerate(images[:-1]):
        audio, duration = get_audio_and_duration(n, audios_path)
        clip_duration = duration - transition_n_frames / fps / 2

        # Generar video con efecto de profundidad
        depth_video_path = generate_depth_effect(str(image_path), str(transitions_path / f"{n}_depth.mp4"), duration=clip_duration)
        
        # Crear clip de video con el efecto de profundidad
        depth_clip = mp.VideoFileClip(depth_video_path)
        
        # Generar transición al siguiente clip
        next_image_path = images[n+1]
        next_audio, next_duration = get_audio_and_duration(n+1, audios_path)
        next_clip_duration = next_duration - transition_n_frames / fps / 2
        next_depth_video_path = generate_depth_effect(str(next_image_path), str(transitions_path / f"{n+1}_depth.mp4"), duration=next_clip_duration)
        next_depth_clip = mp.VideoFileClip(next_depth_video_path)
        
        transition_clip_1, transition_clip_2 = generate_transition(depth_clip, next_depth_clip, transition_n_frames)
        
        full_video = mp.concatenate_videoclips([depth_clip, transition_clip_1, transition_clip_2]).set_audio(audio)
        
        timeline.append(full_video)

    # Procesar la última imagen
    last_audio, last_duration = get_audio_and_duration(len(images)-1, audios_path)
    last_clip_duration = last_duration - transition_n_frames / fps / 2
    last_depth_video_path = generate_depth_effect(str(images[-1]), str(transitions_path / f"{len(images)-1}_depth.mp4"), duration=last_clip_duration)
    last_depth_clip = mp.VideoFileClip(last_depth_video_path)
    last_depth_clip = last_depth_clip.set_audio(last_audio)
    timeline.append(last_depth_clip)

    # Concatenar clips y ajustar duración
    video = mp.concatenate_videoclips(timeline)
    video = adjust_video_duration(video)

    # Escribir archivo de video
    video.write_videofile(str(output_path))


def generate_depth_effect(input_image_path, output_video_path, duration=5, fps=60):
    scene = DepthScene(backend="headless")
    
    estimator = DepthAnythingV2()
    scene.set_estimator(estimator)
    
    image = Image.open(input_image_path)
    depth = estimator.estimate(image)
    
    width, height = image.size
    
    scene.input(image=image, depth=depth)
    scene.aspect_ratio = None
    
    scene.add_animation(
        Presets.Dolly(
            intensity=1,
            reverse=False,
            cumulative=False,
            smooth=False,
            loop=False,
            depth=0.5,
        )
    )
    
    output_path = scene.main(
        width=width,
        height=height,
        ssaa=1.5,
        fps=fps,
        time=duration,
        loop=0,
        output=Path(output_video_path),
        noturbo=(os.getenv("NOTURBO","0")=="1"),
    )[0]
    
    return str(output_path)

if __name__ == "__main__":
    N = 1
    ASSETS_FOLDER = Path('data/MITO_TV/SHORTS/MITOS_NORDICOS/')
    generate_depth_video(
        images_path=ASSETS_FOLDER / f'{N}/images',
        audios_path=ASSETS_FOLDER / f'{N}/audios',
        output_path=ASSETS_FOLDER / f"{N}/{N}.mp4"
    )