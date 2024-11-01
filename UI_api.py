import time
from enum import Enum
from pathlib import Path
from dataclasses import dataclass

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from UI_utils import ProductionStatusManager
from generators.image_generator import ImageGenerator, ImageGenerators
from tools.storyboarder import Storyboarder
from tools.writer import Writer
from generators.LLM import LLM, Models
from generators.TTS import ElevenLabsTTS, Voices
from tools.video_editor import VideoEditor
from data_types import SerieData, VideoData, VideoYoutubeDetails, VideoProductionStatus
from serie_productor import ShortsSerieGenerator

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="templates")

CHANNEL_PATH = Path("./data/MITO_TV")

@dataclass
class Config:
    llm_model: Models = Models.OpenAI.GPT4oMini
    image_generator: ImageGenerator = ImageGenerators.Replicate.FLUX1_SCHNELL
    temperature: float = 0.5
    
    def to_dict(self):
        return {
            "llm_model": str(self.llm_model),
            "image_generator": str(self.image_generator),
            "temperature": self.temperature,
            "available_llm_models": [str(model) for model_class in vars(Models).values() 
                               if isinstance(model_class, type) and issubclass(model_class, Enum)
                               for model in model_class.__members__.values()],
            "available_image_generators": [str(model) for model_class in vars(ImageGenerators).values() 
                    if isinstance(model_class, type) and issubclass(model_class, Enum)
                    for model in model_class.__members__.values()],
        }

config = Config()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    series_data = ProductionStatusManager.get_series_data(channel_path=CHANNEL_PATH)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "series_data": series_data,
    })

@app.get("/config")
async def get_config():
    return JSONResponse(content=config.to_dict())

@app.post("/config")
async def update_config(request: Request):
    config_update = await request.json()
    
    config.llm_model = getattr(getattr(Models, provider := config_update["llm_model"].split('.')[0]), config_update["llm_model"].split('.')[1])
    config.image_generator = getattr(getattr(ImageGenerators, provider := config_update["image_generator"].split('.')[0]), config_update["image_generator"].split('.')[1])
    config.temperature = float(config_update["temperature"])
    return JSONResponse(content=config.to_dict())

@app.get("/create/serie", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("create_serie.html", {
        "request": request,
    })

@app.post("/create/serie")
async def create_serie(request: Request):
    try:
        form_data = await request.json()
        
        llm = LLM(model=config.llm_model, llm_config={"temperature": config.temperature})
        
        serie_dir = CHANNEL_PATH / form_data["name"].lower().replace(" ", "_")
        serie_data = SerieData(
            json_data_path=str(serie_dir / "data.json"),
            serie_path=str(serie_dir),
            name=form_data["name"],
            serie_theme=form_data["serie_theme"],
            used_themes=[],
            expertise=form_data["expertise"],
            num_stories=int(form_data["num_stories"]),
        )
        
        generator = ShortsSerieGenerator(llm=llm, serie_data=serie_data)
        result = generator.generate_serie()
        
        return JSONResponse(content={
            "success": True,
            "message": "Serie generated successfully",
            "result": result.model_dump_json(),
            "serie_path": str(serie_dir)
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Error generating serie: {str(e)}"
            }
        )

@app.post("/create/images/{serie_name}/{video_n}")
async def create_images(request: Request, serie_name: str, video_n: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name.lower().replace(" ", "_") / video_n
    video_data_path = VIDEO_ASSETS_PATH / "video_data.json"
    
    video_data = VideoData.get(video_data_path)

    image_generator = ImageGenerator(generator=config.image_generator)
    image_generator.generate_images(
        prompts=[scene.text for scene in video_data.storyboard.scenes],
        output_dir=VIDEO_ASSETS_PATH / "images",
        width=768,
        height=1344,
        guidance_scale=3.5,
        num_inference_steps=28
    )

@app.get("/storyboard/{serie_name}/{video_n}", response_class=HTMLResponse)
async def show_storyboard(request: Request, serie_name: str, video_n: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name.lower().replace(" ", "_") / video_n
    images_path = VIDEO_ASSETS_PATH / "images"
    video_data_path = VIDEO_ASSETS_PATH / "video_data.json"
    
    video_data = VideoData.get(video_data_path)

    response = templates.TemplateResponse("storyboard.html", {
            "request": request,
            "serie_name": serie_name,
            "video_n": video_n,
            "video_data": video_data.model_dump_json(),
        }
    )
    return response

@app.post("/storyboard/update/{serie_name}/{video_n}/{index}/{field}", response_class=HTMLResponse)
async def update_storyboard(
    request: Request, 
    serie_name: str, 
    video_n: str, 
    index: int,
    field: str
):
    form_data = await request.form()
    new_value = form_data.get(field)
    
    if not new_value:
        raise HTTPException(status_code=400, detail=f"Missing {field} in form data")
    
    storyboard_path = CHANNEL_PATH / serie_name / video_n / "text/storyboard.json"
    
    try:
        Storyboarder.update_storyboard(storyboard_path, [{
            'index': index,
            field: new_value
        }])
        return HTMLResponse(content=f'<p>💾✔️</p>')
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/storyboard/update_image_status/{serie_name}/{video_n}/{index}/{value}", response_class=HTMLResponse)
async def update_image_status(
    request: Request, 
    serie_name: str, 
    video_n: str, 
    index: int,
    value: bool
):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name.lower().replace(" ", "_") / video_n
    video_data_path = VIDEO_ASSETS_PATH / "video_data.json"
    
    video_data = VideoData.get(video_data_path)
    
    # Ensure the list has enough elements
    while len(video_data.production_status.images_completed) <= index:
        video_data.production_status.images_completed.append(False)
    
    video_data.production_status.images_completed[index] = value
    video_data.save()
    
    return HTMLResponse(content=f'<p>💾✔️</p>')

@app.post("/storyboard/remake_image/{serie_name}/{video_n}/{index}", response_class=JSONResponse)
async def remake_image(request: Request, serie_name: str, video_n: str, index: int):
    try:
        form_data = await request.form()
        image_prompt = form_data.get('image')  # Changed from _list[0][1] to get('image')

        VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name.lower().replace(" ", "_") / video_n
        images_dir = VIDEO_ASSETS_PATH / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = images_dir / f"{index}.png"

        # Generate new image using image_generator
        image_generator = ImageGenerator(generator=config.image_generator)
        image_generator.generate_images(
            prompts=[image_prompt],
            output_dir=image_path,
            width=768,
            height=1344,
            guidance_scale=3.5,
            num_inference_steps=28
        )

        # Update storyboard data
        video_data_path = VIDEO_ASSETS_PATH / "video_data.json"
        video_data = VideoData.get(video_data_path)
        
        # Add timestamp to force browser to reload image
        timestamp = int(time.time() * 1000)
        image_url = f"/data/MITO_TV/{serie_name.lower().replace(' ', '_')}/{video_n}/images/{index}.png?t={timestamp}"

        return JSONResponse(content={
            "success": True,
            "url": image_url
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@app.get("/text/{serie_name}/{video_n}", response_class=HTMLResponse)
async def show_text(request: Request, serie_name: str, video_n: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name.lower().replace(" ", "_") / video_n
    text_path = VIDEO_ASSETS_PATH / "text/text.txt"
    
    if not text_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing text file for {serie_name}/{video_n}")

    text_content = text_path.read_text(encoding='utf-8')

    response = templates.TemplateResponse("text.html", {
            "request": request,
            "serie_name": serie_name,
            "video_n": video_n,
            "text_content": text_content,
        }
    )
    return response

@app.post("/text/update/{serie_name}/{video_n}", response_class=HTMLResponse)
async def update_text(request: Request, serie_name: str, video_n: str):
    form_data = await request.form()
    new_text = form_data.get("text")
    
    if not new_text:
        raise HTTPException(status_code=400, detail="Missing text in form data")
    
    text_path = CHANNEL_PATH / serie_name / video_n / "text/text.txt"
    
    try:
        text_path.write_text(new_text, encoding='utf-8')
        return HTMLResponse(content=f'<p>💾✔️</p>')
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/text/generate/{serie_name}/{video_n}", response_class=HTMLResponse)
async def generate_text(request: Request, serie_name: str, video_n: str):
    form_data = await request.form()
    content = form_data.get("content")
    words_number = int(form_data.get("words_number", 100))
    
    if not content:
        raise HTTPException(status_code=400, detail="Missing content in form data")
    
    text_path = CHANNEL_PATH / serie_name / video_n / "text/text.txt"
    
    try:
        writer = Writer(LLM(config.llm_model, llm_config={'temperature': config.temperature}))
        generated_text = writer.generate_story(content=content, words_number=words_number)
        writer.save_text(text=generated_text, save_path=text_path)
        return HTMLResponse(content=generated_text)
    except Exception as e:
        return HTMLResponse(content=f'<p style="color:red;">Error: {str(e)}</p>', status_code=500)

@app.post("/generate_tts/{serie_name}/{video_n}", response_class=HTMLResponse)
async def generate_tts(request: Request, serie_name: str, video_n: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name / video_n
    storyboard_path = VIDEO_ASSETS_PATH / "text/storyboard.json"
    audios_path = VIDEO_ASSETS_PATH / "audios"

    if not storyboard_path.exists():
        raise HTTPException(status_code=404, detail=f"Storyboard not found for {serie_name}/{video_n}")

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

@app.post("/generate_video/{serie_name}/{video_n}", response_class=HTMLResponse)
async def generate_video(request: Request, serie_name: str, video_n: str):
    VIDEO_ASSETS_PATH = CHANNEL_PATH / serie_name / video_n
    images_path = VIDEO_ASSETS_PATH / "images"
    audios_path = VIDEO_ASSETS_PATH / "audios"
    output_path = VIDEO_ASSETS_PATH / f"{video_n}.mp4"

    if not images_path.exists() or not audios_path.exists():
        raise HTTPException(status_code=404, detail=f"Missing images or audios for {serie_name}/{video_n}")

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
