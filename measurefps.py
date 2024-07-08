from pydub import AudioSegment
from mutagen.mp3 import MP3

# Cargar el archivo mp3
audio = MP3("audio.mp3")

# Obtener la duración en segundos
duration_in_seconds = audio.info.length

# Calcular el número de frames a 24 fps
frames = duration_in_seconds * 24

print(f"El número de frames necesarios para cubrir el tiempo del mp3 a 24 fps es: {frames}")