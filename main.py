from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
from contextlib import asynccontextmanager
import os, httpx, tempfile
from PIL import Image
from io import BytesIO

models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    import clip, torch
    models["clip"], models["pre"] = clip.load("ViT-B/32", device="cpu")
    models["torch"] = torch
    yield

app = FastAPI(lifespan=lifespan)

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"]
)

async def fetch_image(url: str) -> Image.Image:
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=15)
    return Image.open(BytesIO(r.content)).convert("RGB")

def run_clip(image: Image.Image):
    import clip
    torch = models["torch"]
    categories = ["food", "sport", "nature", "person", "vehicle", "animal", "art", "technology"]
    tensor = models["pre"](image).unsqueeze(0)
    text = clip.tokenize([f"a photo of {c}" for c in categories])
    with torch.no_grad():
        logits, _ = models["clip"](tensor, text)
        probs = logits.softmax(dim=-1)[0]
    top = probs.argmax().item()
    return categories[top], round(float(probs[top]), 3)

def run_deepface(image: Image.Image):
    try:
        from deepface import DeepFace
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            image.save(f.name)
            result = DeepFace.analyze(f.name, actions=["age", "gender", "emotion"], silent=True)
        r = result[0]
        return {"age": r["age"], "gender": r["dominant_gender"], "emotion": r["dominant_emotion"]}
    except:
        return None

class AnalyzeRequest(BaseModel):
    post_id: str
    image_url: str

@app.get("/")
def root():
    return {"status": "UzaRoom AI server is running"}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    image = await fetch_image(req.image_url)
    clip_category, clip_score = run_clip(image)
    face_data = run_deepface(image)

    supabase.table("post_analysis").insert({
        "post_id": req.post_id,
        "image_url": req.image_url,
        "labels": [clip_category],
        "clip_category": clip_category,
        "clip_score": clip_score,
        "face_data": face_data,
        "is_nsfw": False
    }).execute()

    return {
        "post_id": req.post_id,
        "clip_category": clip_category,
        "clip_score": clip_score,
        "face_data": face_data
    }
