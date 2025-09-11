from fastapi import FastAPI, Request, UploadFile, File, Form # type: ignore 
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from services.llm_service import get_llm_response, get_llm_response_with_files
from typing import List
import os

app = FastAPI()

# Read frontend URL from environment (set in Render dashboard)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Create list of allowed origins
allowed_origins = [
    FRONTEND_URL,
    "https://ai-assistant-trial.netlify.app",  # Your specific Netlify URL
    "https://*.netlify.app",  # Allow all Netlify subdomains (if needed)
    "http://localhost:3000",  # Local development
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # Alternative localhost
]

# Remove duplicates and empty strings
allowed_origins = list(set(filter(None, allowed_origins)))

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "LLM Chatbot Backend Active"}

@app.head("/")
def head_root():
    return JSONResponse({"message": "OK"})

@app.options("/chat")
def chat_options():
    return JSONResponse({"message": "OK"})

@app.options("/chat-with-files")
def chat_with_files_options():
    return JSONResponse({"message": "OK"})

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message", "")
        bot_response = await get_llm_response(user_message)
        return {"response": bot_response}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Internal server error"}
        )

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
        return JSONResponse(
            status_code=500,
            content={
                "response": f"Sorry, I encountered an error processing your files: {str(e)}",
                "error": True
            }
        )