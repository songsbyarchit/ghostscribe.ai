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

def apply_edit_to_doc(doc_id: str, command: dict):
    service = get_docs_service()
    action = command.get("action")
    text = command.get("text")
    target = command.get("target")

    try:
        if action == "insert":
            requests = [{
                "insertText": {
                    "location": { "index": 1 },
                    "text": text + "\n"
                }
            }]
            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            print(f"[INSERT] '{text}' at top")
            return True

        elif action == "delete":
            # Fetch doc content to find position of inserted text
            doc = service.documents().get(documentId=doc_id).execute()
            content = doc.get("body", {}).get("content", [])
            full_text = ""
            index = 1
            for element in content:
                if "paragraph" in element:
                    for elem in element["paragraph"]["elements"]:
                        text_run = elem.get("textRun", {}).get("content", "")
                        if text in text_run:
                            start = index
                            end = index + len(text)
                            requests = [{
                                "deleteContentRange": {
                                    "range": {
                                        "startIndex": start,
                                        "endIndex": end
                                    }
                                }
                            }]
                            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
                            print(f"[DELETE] '{text}' from index {start}")
                            return True
                        index += len(text_run)

            print("[DELETE] Text not found")
            return False

        elif action == "replace":
            requests = [{
                "replaceAllText": {
                    "containsText": {
                        "text": target,
                        "matchCase": False
                    },
                    "replaceText": text
                }
            }]
            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()
            print(f"[REPLACE] '{target}' → '{text}'")
            return True

        else:
            print(f"[SKIPPED] Unknown action: {action}")
            return False

    except Exception as e:
        print(f"[ERROR]: {e}")
        return False