from fastapi import FastAPI
from pydantic import BaseModel
from supabase import create_client
import os, httpx

app = FastAPI()

supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_SERVICE_ROLE_KEY"]
)

class AnalyzeRequest(BaseModel):
    post_id: str
    image_url: str

@app.get("/")
def root():
    return {"status": "UzaRoom AI server is running"}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    # فعلاً mock — بعداً YOLO/CLIP اضافه می‌شه
    labels = ["person", "outdoor"]
    is_nsfw = False

    supabase.table("post_analysis").insert({
        "post_id": req.post_id,
        "image_url": req.image_url,
        "labels": labels,
        "is_nsfw": is_nsfw
    }).execute()

    return {"post_id": req.post_id, "labels": labels, "is_nsfw": is_nsfw}
