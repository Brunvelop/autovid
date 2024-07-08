import os
import random
import tempfile

import moviepy.editor as mp
import moviepy.video.fx.all as vfx
import cv2
import math
import numpy
from PIL import Image

import vid_transition


def add_positional_noise(clip, noise_level=5, inertia=0.9):
    last_dx = 0
    last_dy = 0

    def effect(get_frame, t):
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


def zoom_in_face_effect(clip, zoom_ratio=0.04, face_zoom=True):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def effect(get_frame, t):
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

def get_size(aspect_ratio):
    if aspect_ratio == '9:16':
        return (720, 1280)
    elif aspect_ratio == '16:9':
        return (1920, 1080)

def clear_transitions_folder():
    os.makedirs('./tmp/transitions', exist_ok=True)
    for file in os.listdir('./tmp/transitions'):
        os.remove(os.path.join('./tmp/transitions', file))

def get_audio_and_duration(n, audios_path):
    audio = mp.AudioFileClip(os.path.join(audios_path, str(n) + ".mp3"))
    audio = audio.set_duration(audio.duration - 0.2)
    duration = audio.duration + 0.2
    return audio, duration

def get_clip(pre_clip, aspect_ratio, size):
    if aspect_ratio == '9:16':
        return vfx.crop(
            pre_clip,
            width=int(pre_clip.size[1]*9/16), height=int(pre_clip.size[1]),
            x_center=int(pre_clip.size[0]/2), y_center=int(pre_clip.size[1]/2)
        ).resize(size)
    elif aspect_ratio == '16:9':
        return vfx.crop(
            pre_clip,
            width=int(pre_clip.size[0]), height=int(pre_clip.size[0]*16/9),
            x_center=int(pre_clip.size[0]/2), y_center=int(pre_clip.size[1]/2)
        ).resize(size)

def generate_transition(slide1, slide2, num_frames):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir='./tmp/transitions') as temp1, \
        tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir='./tmp/transitions') as temp2, \
        tempfile.NamedTemporaryFile(suffix=".mp4", delete=False, dir='./tmp/transitions') as temp_transition:

        slide1.write_videofile(temp1.name)
        slide2.write_videofile(temp2.name)

        animations = ["rotation", "rotation_inv", "zoom_in", "zoom_out", "translation", "translation_inv"]
        vid_transition.main(
            input_videos=[temp1.name, temp2.name],
            num_frames=num_frames,  # Número de frames para la transición
            output=temp_transition.name,  # Ruta de salida para el video de transición
            animation=random.choice(animations),  # Tipo de animación
            max_rotation=45,  # Máxima rotación para la animación de rotación
            max_distortion=0.7,  # Máxima distorsión para la animación
            max_blur=0.2,  # Máximo desenfoque para la animación
            max_brightness=1.0,  # Máximo brillo para la animación
            max_zoom=2.0,  # Máximo zoom para la animación
            debug=False,  # Modo de depuración
            art=False,  # Mostrar arte ASCII
            remove=False,  # Eliminar videos originales después de la transición
            merge=False  # Fusionar fases de video en un solo archivo
        )

        transition_clip_1 = mp.VideoFileClip(temp_transition.name.rsplit('.', 1)[0] + "_phase1.mp4")
        transition_clip_2 = mp.VideoFileClip(temp_transition.name.rsplit('.', 1)[0] + "_phase2.mp4")
        print(f"Transition clips: {transition_clip_1, transition_clip_2}")

        return transition_clip_1, transition_clip_2

def adjust_video_duration(video):
    if video.duration >= 59:
        return video.fx(vfx.speedx, video.duration/59).set_fps(30)
    return video

def generate_video(fps=30, transition_n_frames=6, images_path='tmp/images', audios_path='tmp/audios', output_path='output/video.mp4'):
    clear_transitions_folder()

    images = os.listdir(images_path)
    timeline = []
    for n, image in enumerate(images[:-1]):  # Excluimos la última imagen porque no tiene una imagen siguiente para la transición

        image_clip_1 = mp.ImageClip(os.path.join(images_path, image)).set_fps(30)
        audio_1, duration_1 = get_audio_and_duration(n, audios_path)
        image_clip_1 = image_clip_1.set_duration(duration_1 -  transition_n_frames / fps / 2)
        image_clip_1 = zoom_in_face_effect(image_clip_1)

        image_clip_2 = mp.ImageClip(os.path.join(images_path, images[n+1])).set_fps(30)
        audio_2, duration_2 = get_audio_and_duration(n+1, audios_path)
        image_clip_2 = image_clip_2.set_duration(duration_2 -  transition_n_frames / fps / 2)

        transition_clip_1, transition_clip_2 = generate_transition(image_clip_1, image_clip_2, transition_n_frames)
        full_video_1 = mp.concatenate_videoclips([image_clip_1, transition_clip_1, transition_clip_2]).set_audio(audio_1)
        
        timeline.append(full_video_1)

    image_clip_last = mp.ImageClip(os.path.join(images_path, images[n+1])).set_fps(30)
    audio_last, duration_last = get_audio_and_duration(n+1, audios_path)
    image_clip_last = image_clip_2.set_duration(duration_last -  transition_n_frames / fps / 2)
    image_clip_last = zoom_in_face_effect(image_clip_last)
    image_clip_last = image_clip_last.set_audio(audio_last)
    timeline.append(image_clip_last)

    # Concatenar clips y ajustar duración
    video = mp.concatenate_videoclips(timeline)
    video = adjust_video_duration(video)

    # Aplicar efecto de ruido como postprocesado
    video = add_positional_noise(video, noise_level=10, inertia=0.7)

    # Escribir archivo de video
    video.write_videofile(output_path)