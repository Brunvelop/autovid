import time
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from UI_utils import ProductionStatusManager
from generators.image_generator import ReplicateFluxDev
from tools.storyboarder import Storyboarder
from tools.writer import Writer
from generators.LLM import LLM, Models
from generators.TTS import ElevenLabsTTS, Voices
from tools.video_editor import VideoEditor

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="templates")

CHANNEL_PATH = Path("./data/MITO_TV")

@dataclass
class Config:
    llm_model: Models = Models.Anthropic.CLAUDE_3_5_sonnet
    temperature: float = 0.5
    
    def to_dict(self):
        return {
            "llm_model": str(self.llm_model),
            "temperature": self.temperature,
            "available_models": [str(model) for model_class in vars(Models).values() 
                               if isinstance(model_class, type) and issubclass(model_class, Enum)
                               for model in model_class.__members__.values()]
        }

config = Config()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    global_status = ProductionStatusManager.get_global_status(channel_path=CHANNEL_PATH)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "global_status": global_status,
    })

@app.get("/config")
async def get_config():
    return JSONResponse(content=config.to_dict())

@app.post("/config")
async def update_config(request: Request):
    config_update = await request.json()
    
    config.llm_model = getattr(getattr(Models, provider := config_update["llm_model"].split('.')[0]), config_update["llm_model"].split('.')[1])
    config.temperature = float(config_update["temperature"])
    return JSONResponse(content=config.to_dict())

@app.get("/create/serie", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("create_serie.html", {
        "request": request,
    })

@app.get("/storyboard/{short_category}/{short_num}", response_class=HTMLResponse)
async def show_storyboard(request: Request, short_category: str, short_num: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / short_category / short_num
    images_path = VIDEO_ASSETS_PATH / "images"
    storyboard_path = VIDEO_ASSETS_PATH / "text/storyboard.json"
    status_path = VIDEO_ASSETS_PATH / "status.json"
    
    if not images_path.exists() or not storyboard_path.exists() or not status_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing assets for {short_category}/{short_num}")

    storyboard = Storyboarder.load_storyboard(storyboard_path)

    scenes = []
    for idx, image in enumerate(sorted(images_path.iterdir(), key=lambda x: int(x.stem))):
        scene = {
            'image_url': "/" + (images_path / image.name).as_posix(),
            'text': storyboard[idx].get('text', ''),
            'image_prompt': storyboard[idx].get('image', ''),
            'audio_url': "/" + (VIDEO_ASSETS_PATH / "audios" / f"{image.stem}.mp3").as_posix(),
        }
        scenes.append(scene)

    writer = Writer(LLM(config.llm_model, llm_config={'temperature': config.temperature}))
    response = templates.TemplateResponse("storyboard.html", {
            "request": request,
            "short_category": short_category,
            "short_num": short_num,
            "scenes": scenes,
            "status": VideoProductionStatus.get(status_path=status_path, writer=writer)
        }
    )
    return response

@app.post("/storyboard/update_image_status/{short_category}/{short_num}/{image_index}/{is_completed}")
async def update_image_status(
    request: Request,
    short_category: str, 
    short_num: str, 
    image_index: int, 
    is_completed: str,
):
    status_path = CHANNEL_PATH / short_category / short_num / "status.json"
    
    try:
        ProductionStatusManager.update_image_status(status_path, image_index, is_completed == 'true')
        status_symbol = '✔️' if is_completed == 'true' else '❌'
        return HTMLResponse(content=f'<h2 id="status{image_index}">{status_symbol}</h2>')
    except Exception as e:
        return HTMLResponse(
            content=f'<h2 id="status{image_index}" style="color:red;">Error</h2>',
            status_code=500
        )

@app.post("/storyboard/update/{short_category}/{short_num}/{index}/{field}", response_class=HTMLResponse)
async def update_storyboard(
    request: Request, 
    short_category: str, 
    short_num: str, 
    index: int,
    field: str
):
    form_data = await request.form()
    new_value = form_data.get(field)
    
    if not new_value:
        raise HTTPException(status_code=400, detail=f"Missing {field} in form data")
    
    storyboard_path = CHANNEL_PATH / short_category / short_num / "text/storyboard.json"
    
    try:
        Storyboarder.update_storyboard(storyboard_path, [{
            'index': index,
            field: new_value
        }])
        return HTMLResponse(content=f'<p>💾✔️</p>')
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/storyboard/remake_image/{short_category}/{short_num}/{index}", response_class=HTMLResponse)
async def remake_image(request: Request, short_category: str, short_num: str, index: int):
    form_data = await request.form()
    image_prompt = form_data._list[0][1]

    VIDEO_ASSETS_PATH = CHANNEL_PATH / short_category / short_num
    image_path = VIDEO_ASSETS_PATH / "images" / f"{index}.png"

    # Generate new image using image_generator
    image_generator = ReplicateFluxDev(verbose=True)
    image_generator.generate_images(
        prompts=[image_prompt],
        output_dir=image_path,
        width=768,
        height=1344,
        guidance_scale=3.5,
        num_inference_steps=28
    )

    # Use a timestamp for the cache-buster
    timestamp = int(time.time() * 1000)  # Use milliseconds for more uniqueness
    image_url = f"/{image_path.as_posix()}?t={timestamp}"

    # Return updated image HTML with the unique URL, wrapped in a div with the correct ID
    return HTMLResponse(content=f'<div id="image{index}"><img src="{image_url}" class="w-full" onload="this.style.opacity=1"></div>')

@app.get("/text/{short_category}/{short_num}", response_class=HTMLResponse)
async def show_text(request: Request, short_category: str, short_num: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / short_category / short_num
    text_path = VIDEO_ASSETS_PATH / "text/text.txt"
    
    if not text_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing text file for {short_category}/{short_num}")

    text_content = text_path.read_text(encoding='utf-8')

    response = templates.TemplateResponse("text.html", {
            "request": request,
            "short_category": short_category,
            "short_num": short_num,
            "text_content": text_content,
        }
    )
    return response

@app.post("/text/update/{short_category}/{short_num}", response_class=HTMLResponse)
async def update_text(request: Request, short_category: str, short_num: str):
    form_data = await request.form()
    new_text = form_data.get("text")
    
    if not new_text:
        raise HTTPException(status_code=400, detail="Missing text in form data")
    
    text_path = CHANNEL_PATH / short_category / short_num / "text/text.txt"
    
    try:
        text_path.write_text(new_text, encoding='utf-8')
        return HTMLResponse(content=f'<p>💾✔️</p>')
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/text/generate/{short_category}/{short_num}", response_class=HTMLResponse)
async def generate_text(request: Request, short_category: str, short_num: str):
    form_data = await request.form()
    content = form_data.get("content")
    words_number = int(form_data.get("words_number", 100))
    
    if not content:
        raise HTTPException(status_code=400, detail="Missing content in form data")
    
    text_path = CHANNEL_PATH / short_category / short_num / "text/text.txt"
    
    try:
        writer = Writer(LLM(config.llm_model, llm_config={'temperature': config.temperature}))
        generated_text = writer.generate_story(content=content, words_number=words_number)
        writer.save_text(text=generated_text, save_path=text_path)
        return HTMLResponse(content=generated_text)
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/generate_tts/{short_category}/{short_num}", response_class=HTMLResponse)
async def generate_tts(request: Request, short_category: str, short_num: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / short_category / short_num
    storyboard_path = VIDEO_ASSETS_PATH / "text/storyboard.json"
    audios_path = VIDEO_ASSETS_PATH / "audios"

    if not storyboard_path.exists():
        raise HTTPException(status_code=404, detail=f"Storyboard not found for {short_category}/{short_num}")

    storyboard = Storyboarder.load_storyboard(storyboard_path)

    try:
        for idx, scene in enumerate(storyboard):
            text = scene.get('text', '')
            output_file = audios_path / f"{idx}.mp3"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            ElevenLabsTTS.generate_speech(
                text=text,
                output_file=output_file,
                voice=Voices.ElevenLabs.DAN_DAN
            )
        return HTMLResponse(content="<p>✅ TTS generation completed</p>")
    except Exception as e:
        return HTMLResponse(content=f"<p style='color:red;'>Error generating TTS: {str(e)}</p>", status_code=500)

@app.post("/generate_video/{short_category}/{short_num}", response_class=HTMLResponse)
async def generate_video(request: Request, short_category: str, short_num: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / short_category / short_num
    images_path = VIDEO_ASSETS_PATH / "images"
    audios_path = VIDEO_ASSETS_PATH / "audios"
    output_path = VIDEO_ASSETS_PATH / f"{short_num}.mp4"

    if not images_path.exists() or not audios_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing images or audios for {short_category}/{short_num}")

    try:
        VideoEditor.generate_depth_video(
            images_path=images_path,
            audios_path=audios_path,
            output_path=output_path,
            background_music_path=Path("C:/Users/bruno/Desktop/autovid/music/mito_tv_loop_01.mp3")
        )
        video_url = "/" + output_path.as_posix()
        return HTMLResponse(content=f"<p>✅ Video generation completed. <a href='{video_url}' target='_blank'>Watch Video</a></p>")
    except Exception as e:
        return HTMLResponse(content=f"<p style='color:red;'>Error generating video: {str(e)}</p>", status_code=500)
