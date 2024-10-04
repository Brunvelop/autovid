#uvicorn UI_api:app --reload
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from UI_utils import ProductionStatusManager, VideoStatus
from image_generator import ReplicateFluxDev
from storyboarder import Storyboarder

app = FastAPI()
app.mount("/data", StaticFiles(directory="data"), name="data")
templates = Jinja2Templates(directory="templates")

BASE_SHORTS_PATH = Path("./data/MITO_TV/SHORTS")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    global_status = ProductionStatusManager.get_global_status(shorts_path=BASE_SHORTS_PATH)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "global_status": global_status,
    })

@app.get("/storyboard/{short_category}/{short_num}", response_class=HTMLResponse)
async def show_storyboard(request: Request, short_category: str, short_num: str):
    VIDEO_ASSETS_PATH = BASE_SHORTS_PATH / short_category / short_num
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

    response = templates.TemplateResponse("storyboard.html", {
            "request": request,
            "short_category": short_category,
            "short_num": short_num,
            "scenes": scenes,
            "status": VideoStatus.get(status_path=status_path)
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
    status_path = BASE_SHORTS_PATH / short_category / short_num / "status.json"
    
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
    
    storyboard_path = BASE_SHORTS_PATH / short_category / short_num / "text/storyboard.json"
    
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

    VIDEO_ASSETS_PATH = BASE_SHORTS_PATH / short_category / short_num
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

    # Add a unique query parameter to the image URL to avoid caching
    unique_string = f"{short_category}_{short_num}_{index}_{image_prompt}"
    cache_buster = hash(unique_string)
    image_url = f"/{image_path.as_posix()}?cb={cache_buster}"

    # Return updated image HTML with the unique URL
    return HTMLResponse(content=f'<img src="{image_url}" class="w-full">')