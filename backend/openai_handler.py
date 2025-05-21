from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from openai_handler import interpret_command
from google_docs import apply_edit_to_doc

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOC_ID = os.getenv("DOC_ID")

# In-memory edit history for undo
edit_history = []
MAX_HISTORY = 10

def remember_edit(action_type, content, location=None):
    if len(edit_history) >= MAX_HISTORY:
        edit_history.pop(0)
    edit_history.append({
        "action": action_type,
        "text": content,
        "location": location
    })

def undo_last_edit():
    if not edit_history:
        return "Nothing to undo"
    last = edit_history.pop()
    if last["action"] == "insert":
        # Just reinserted at top, so delete same text
        return apply_edit_to_doc(DOC_ID, {"action": "delete", "text": last["text"], "target": "last_inserted_text"})
    return "Undo not implemented for this type"

@app.get("/")
def read_root():
    return {"message": "Ghostscribe API is live"}

@app.post("/transcribe")
async def transcribe(request: Request):
    data = await request.json()
    transcript = data.get("transcript")
    print(f"[VOICE BLOCK]: {transcript}")

    parsed = interpret_command(transcript)
    action = parsed.get("action")
    text = parsed.get("text")
    target = parsed.get("target")

    if action == "insert" and text:
        success = apply_edit_to_doc(DOC_ID, {
            "action": "insert",
            "text": text
        })
        if success:
            remember_edit("insert", text)
        return {"status": "inserted", "text": text}

    elif action == "delete" and target == "last_inserted_text":
        if edit_history:
            last = edit_history[-1]
            success = apply_edit_to_doc(DOC_ID, {
                "action": "delete",
                "text": last["text"]
            })
            if success:
                edit_history.pop()
            return {"status": "deleted", "text": last["text"]}
        return {"status": "nothing_to_delete"}

    elif action == "undo":
        result = undo_last_edit()
        return {"status": "undo", "result": result}

    elif action == "replace" and text and target:
        success = apply_edit_to_doc(DOC_ID, {
            "action": "replace",
            "text": text,
            "target": target
        })
        return {"status": "replaced", "from": target, "to": text}

    return {"status": "ignored", "reason": "Unsupported or empty command"}