from pydub import AudioSegment

# Cargar archivo de audio
audio = AudioSegment.from_mp3("out4.mp3")

# Obtener duración en milisegundos
duracion_ms = len(audio)

# Convertir duración a segundos
duracion_s = duracion_ms / 1000.0

# Calcular número de frames a 24 fps
frames = duracion_s * 24

print(f"Se necesitan {frames} frames para rellenar el audio.")


import os
from pydub import AudioSegment

# Directorio de los archivos de audio
directorio = 'music'

# Obtener lista de todos los archivos mp3 en el directorio
archivos_mp3 = [f for f in os.listdir(directorio) if f.endswith('.mp3')]

# Procesar cada archivo de audio
for archivo in archivos_mp3:
    # Cargar archivo de audio
    audio = AudioSegment.from_mp3(os.path.join(directorio, archivo))

    # Obtener duración en milisegundos
    duracion_ms = len(audio)

    # Convertir duración a segundos
    duracion_s = duracion_ms / 1000.0

    # Calcular número de frames a 24 fps
    frames = duracion_s * 24

    print(f"Se necesitan {frames} frames para rellenar el audio de {archivo}.")