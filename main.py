from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai, os, base64

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

@app.post("/", response_class=HTMLResponse)
async def analyze_image(request: Request, image: UploadFile = File(...)):
    os.makedirs("static/uploads", exist_ok=True)
    fp = f"static/uploads/{image.filename}"
    with open(fp, "wb") as f:
        f.write(await image.read())

    b64 = base64.b64encode(open(fp, "rb").read()).decode()
    try:
        resp = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": "Deskripsikan gambar ini secara visual detail, untuk prompt generator."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]}
            ],
            max_tokens=500
        )
        result = resp.choices[0].message.content
    except Exception as e:
        result = f"Error: {e}"

    return templates.TemplateResponse("index.html", {"request": request, "result": result})
