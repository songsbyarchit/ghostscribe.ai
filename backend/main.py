from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

edit_history = []
MAX_HISTORY = 10

def remember_edit(action_type, content, location):
    if len(edit_history) >= MAX_HISTORY:
        edit_history.pop(0)
    edit_history.append({
        "action": action_type,
        "content": content,
        "location": location
    })

@app.get("/")
def read_root():
    return {"message": "Ghostscribe API is live"}

@app.post("/transcribe")
async def transcribe(request: Request):
    data = await request.json()
    transcript = data.get("transcript")
    print(f"[VOICE BLOCK]: {transcript}")
    return {"status": "received", "text": transcript}