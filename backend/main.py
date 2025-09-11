from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from services.llm_service import get_llm_response, get_llm_response_with_files
from typing import List, Optional
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
        # Process the uploaded files
        file_contents = []
        file_info = []
        
        for file in files:
            content = await file.read()
            file_info.append({
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content)
            })
            
            # Handle different file types
            if file.content_type.startswith('text/') or file.content_type == 'application/json':
                # Text files
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
                # Image files - you might want to add image processing here
                file_contents.append({
                    "filename": file.filename,
                    "type": "image", 
                    "content": f"Image file: {file.filename} ({len(content)} bytes)"
                })
            else:
                # Other file types
                file_contents.append({
                    "filename": file.filename,
                    "type": "other",
                    "content": f"File: {file.filename} ({file.content_type}, {len(content)} bytes)"
                })
        
        # Get LLM response with file context
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