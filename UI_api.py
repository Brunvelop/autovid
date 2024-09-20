#uvicorn UI_api:app --reload
import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from UI_utils import ProductionStatusManager

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="templates")

BASE_SHORTS_PATH = Path("data/MITO_TV/SHORTS/")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    global_status = ProductionStatusManager.get_global_status(shorts_path=BASE_SHORTS_PATH)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "global_status": global_status,
    })

@app.get("/video/{short_category}/{short_num}", response_class=HTMLResponse)
async def show_video(request: Request, short_category: str, short_num: str):
    images_path = BASE_SHORTS_PATH / short_category / short_num / "images"
    text_path = BASE_SHORTS_PATH / short_category / short_num / "text/storyboard.json"
    status_path = BASE_SHORTS_PATH / short_category / short_num / "status.json"
    status = ProductionStatusManager.get_video_status(status_path=status_path)
    
    if not images_path.exists() or not text_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró el mito {short_category}/{short_num}")

    storyboard_texts = json.loads(text_path.read_text(encoding='utf-8'))

    scenes = []
    for idx, image in enumerate(sorted(images_path.iterdir())):
        image_url = f"/data/MITO_TV/SHORTS/{short_category}/{short_num}/images/{image.name}"
        text = storyboard_texts[idx].get('text', '') 
        image_prompt = storyboard_texts[idx].get('image', '')
        
        scene = {
            'image_url': image_url,
            'text': text,
            'image_prompt': image_prompt
        }
        scenes.append(scene)



    response = templates.TemplateResponse("video.html", {
            "request": request,
            "short_category": short_category,
            "short_num": short_num,
            "scenes": scenes,
            "status": status
        }
    )
    
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/update_status/{short_category}/{short_num}/{image_index}/{is_completed}")
async def update_status(
    short_category: str, 
    short_num: str, 
    image_index: int, 
    is_completed: str,
    request: Request
):
    status_path = BASE_SHORTS_PATH / short_category / short_num / "status.json"
    
    try:
        ProductionStatusManager.update_video_status(status_path, image_index, is_completed == 'true')
        return JSONResponse(content={"success": True})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))