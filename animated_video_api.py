import json
import urllib
from urllib import request, parse
import websocket
import uuid

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request(f"http://{server_address}/prompt", data=data)
    try:
        response = request.urlopen(req)
        return json.loads(response.read())
    except urllib.error.HTTPError as e:
        print('Error code: ', e.code)
        print('Reason: ', e.reason)

import random

def modify_workflow(batch_size, max_frames, text):
    with open('comfyUI_api_workflows/animation.json', 'r', encoding='utf-8') as file:
        prompt_workflow = json.load(file)

    # Modificar batch_size y max_frames
    prompt_workflow["9"]["inputs"]["batch_size"] = batch_size
    prompt_workflow["38"]["inputs"]["max_frames"] = max_frames

    # Modificar texto
    prompt_workflow["38"]["inputs"]["text"] = text

    # Modificar seed a un número aleatorio
    prompt_workflow["7"]["inputs"]["seed"] = random.randint(0, 1000000)

    return prompt_workflow

# Definir los nuevos valores
duration = 100
new_batch_size = duration
new_max_frames = duration
new_text = "\"0\": \"love.\""

# Modificar el flujo de trabajo y ponerlo en cola
modified_workflow = modify_workflow(new_batch_size, new_max_frames, new_text)
ws = websocket.WebSocket()
ws.connect(f"ws://{server_address}/ws?clientId={client_id}")
prompt_id = queue_prompt(modified_workflow)['prompt_id']

while True:
    message = ws.recv()
    if isinstance(message, str):
        message = json.loads(message)
        if message['type'] == 'executing' and message['data']['prompt_id'] == prompt_id and message['data']['node'] is None:
            break

ws.close()  # Cerrar la conexión WebSocket