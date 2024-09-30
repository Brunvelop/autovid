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
    for idx, image in enumerate(sorted(images_path.iterdir(), key=lambda x: int(x.stem))):
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
        status_symbol = '✔️' if is_completed == 'true' else '❌'
        return HTMLResponse(content=f'<h2 id="status{image_index}">{status_symbol}</h2>')
    except Exception as e:
        # Devuelve un mensaje de error que HTMX puede manejar
        return HTMLResponse(
            content=f'<h2 id="status{image_index}" style="color:red;">Error</h2>',
            status_code=500
        )


@app.post("/save_storyboard/{short_category}/{short_num}/{index}", response_class=HTMLResponse)
async def save_storyboard(
    request: Request,
    short_category: str,
    short_num: str,
    index: int
):
    form_data = await request.form()
    new_text = form_data.get('text')
    
    text_path = BASE_SHORTS_PATH / short_category / short_num / "text/storyboard.json"
    
    try:
        with open(text_path, 'r', encoding='utf-8') as f:
            storyboard_texts = json.load(f)
        
        storyboard_texts[index]['text'] = new_text
        
        with open(text_path, 'w', encoding='utf-8') as f:
            json.dump(storyboard_texts, f, ensure_ascii=False, indent=2)
        
        return HTMLResponse(content=f'<p>💾✔️</p>')
    except Exception as e:
        return HTMLResponse(
            content=f'<p id="text{index + 1}" style="color:red;">Error al guardar: {str(e)}</p>',
            status_code=500
        )