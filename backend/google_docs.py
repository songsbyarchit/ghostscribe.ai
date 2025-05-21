from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/documents']

def get_docs_service():
    creds = service_account.Credentials.from_service_account_file(
        "backend/credentials.json", scopes=SCOPES
    )
    return build("docs", "v1", credentials=creds)

def apply_edit_to_doc(doc_id: str, command: str):
    service = get_docs_service()

    requests = [
        {
            "insertText": {
                "location": {"index": 1},  # top of the doc
                "text": command + "\n"
            }
        }
    ]

    try:
        response = service.documents().batchUpdate(
            documentId=doc_id,
            body={"requests": requests}
        ).execute()
        print(f"[EDIT SUCCESS] Added: {command}")
        return True
    except Exception as e:
        print(f"[EDIT FAIL] {e}")
        return False