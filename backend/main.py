from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Ghostscribe API is live"}

@app.post("/transcribe")
async def transcribe(request: Request):
    data = await request.json()
    transcript = data.get("transcript")
    return {"status": "ok", "received": transcript}
