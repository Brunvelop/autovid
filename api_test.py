import requests
import json
import base64
from PIL import Image
import io

url = "http://ec2-107-23-131-11.compute-1.amazonaws.com/predictions"
headers = {
    "Content-Type": "application/json"
}
data = {
    "input": {
        "prompt": "a tiny astronaut hatching from an egg on the moon",
        "aspect_ratio": "1:1",
        "num_outputs": 4,
        "seed": None,
        "output_format": "png",
        "output_quality": 80,
        "disable_safety_checker": False
    }
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 200:
    print("Predicción exitosa:")
    response_data = response.json()
    print(json.dumps(response_data, indent=2))
    
    # Procesar y guardar las imágenes
    for i, image_data in enumerate(response_data['output']):
        if image_data.startswith('data:'):
            # Eliminar el prefijo de datos y obtener solo la parte base64
            image_data = image_data.split(',', 1)[1]
        
        # Decodificar la imagen base64
        image_bytes = base64.b64decode(image_data)
        
        # Abrir la imagen con Pillow
        image = Image.open(io.BytesIO(image_bytes))
        
        # Guardar la imagen como PNG
        output_filename = f"output_image_{i+1}.png"
        image.save(output_filename, "PNG")
        print(f"Imagen guardada como {output_filename}")
else:
    print(f"Error en la petición: {response.status_code}")
    print(response.text)