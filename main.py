from fastapi import FastAPI
from pydantic import BaseModel
import os
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class AnalyzeRequest(BaseModel):
    image_url: str
    post_id: str

@app.get("/")
def home():
    return {"status": "UzaRoom AI server is running"}

@app.post("/analyze")
def analyze_image(data: AnalyzeRequest):
    tags = ["test", "photo", "general"]
    category = "general"

    supabase.table("post_ai_tags").insert({
        "post_id": data.post_id,
        "image_url": data.image_url,
        "tags": tags,
        "category": category
    }).execute()

    return {
        "success": True,
        "post_id": data.post_id,
        "tags": tags,
        "category": category
    }
