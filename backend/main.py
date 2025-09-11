from fastapi import FastAPI, Request, UploadFile, File, Form # type: ignore 
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from services.llm_service import get_llm_response, get_llm_response_with_files
from typing import List
import os

app = FastAPI()

# Read frontend URL from environment (set in Render dashboard)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],   # Restrict to your Netlify URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "LLM Chatbot Backend Active"}

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message", "")
    bot_response = await get_llm_response(user_message)
    return {"response": bot_response}

@app.post("/chat-with-files")
async def chat_with_files(
    message: str = Form(""),
    files: List[UploadFile] = File(...)
):
    try:
        file_contents = []
        file_info = []

        for file in files:
            content = await file.read()
            file_info.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            })

            if file.content_type.startswith('text/') or file.content_type == 'application/json':
                try:
                    text_content = content.decode('utf-8')
                    file_contents.append({
                        "filename": file.filename,
                        "type": "text",
                        "content": text_content
                    })
                except UnicodeDecodeError:
                    file_contents.append({
                        "filename": file.filename,
                        "type": "binary",
                        "content": f"Binary file with {len(content)} bytes"
                    })
            elif file.content_type.startswith('image/'):
                file_contents.append({
                    "filename": file.filename,
                    "type": "image",
                    "content": f"Image file: {file.filename} ({len(content)} bytes)"
                })
            else:
                file_contents.append({
                    "filename": file.filename,
                    "type": "other",
                    "content": f"File: {file.filename} ({file.content_type}, {len(content)} bytes)"
                })

        bot_response = await get_llm_response_with_files(message, file_contents)

        return {
            "response": bot_response,
            "files_processed": file_info
        }

    except Exception as e:
        return {
            "response": f"Sorry, I encountered an error processing your files: {str(e)}",
            "error": True
        }
