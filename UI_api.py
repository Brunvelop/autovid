#uvicorn UI_api:app --reload
import os
import json
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Montar archivos estáticos (imágenes)
app.mount("/data", StaticFiles(directory="data"), name="data")

# Ruta base
BASE_SHORTS_PATH = Path("data/MITO_TV/SHORTS/")
SHORTS_STATE_PATH = BASE_SHORTS_PATH / "state_shorts.json"

# Configurar las plantillas de Jinja2
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup_event():
    if SHORTS_STATE_PATH.is_file():
        return
    
    state_shorts = {}
    for category in Path(BASE_SHORTS_PATH).iterdir():
        if category.is_dir():
            state_shorts[category.name] = {}
            for mito in sorted(category.iterdir(), key=lambda x: int(x.name)):
                if mito.is_dir():
                    state_shorts[category.name][mito.name] = {"completed": False}
    
    with SHORTS_STATE_PATH.open('w') as file:
        json.dump(state_shorts, file, indent=4)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    with SHORTS_STATE_PATH.open('r') as file:
        state_shorts = json.load(file)

    categories = sorted([
        d.name for d in BASE_SHORTS_PATH.iterdir()
        if d.is_dir()
    ])

    # Obtener lista de mitos por categoría
    shorts_by_category = {}
    for category in categories:
        category_path = BASE_SHORTS_PATH / category
        shorts_by_category[category] = sorted([
            d.name for d in category_path.iterdir()
            if d.is_dir()
        ])

    return templates.TemplateResponse("index.html", {
        "request": request,
        "mitos_por_categoria": shorts_by_category,
        "estado_mitos": state_shorts
    })

@app.get("/video/{short_category}/{short_num}", response_class=HTMLResponse)
async def show_video(request: Request, short_category: str, short_num: str):
    images_path = BASE_SHORTS_PATH / short_category / short_num / "images"
    if not images_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró el mito {short_category}/{short_num}")

    images_urls = [str(image.relative_to(BASE_SHORTS_PATH.parent)) for image in sorted(images_path.iterdir())]
    return templates.TemplateResponse(
        "video.html",
        {
            "request": request,
            "tipo_mito": short_category,
            "mito_num": short_num,
            "images": images_urls
        }
    )