from fastapi import FastAPI, Request, UploadFile, File, Form # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.responses import JSONResponse # type: ignore
from services.llm_service import get_llm_response, get_llm_response_with_files
from typing import List
import os
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Read frontend URL from environment (set in Render dashboard)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Create list of allowed origins
allowed_origins = [
    FRONTEND_URL,
    "https://ai-assistant-trial.netlify.app",
    "https://*.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
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
        logger.info("Received chat request")
        
        # Log the raw request for debugging
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        # Parse JSON
        try:
            data = await request.json()
            logger.info(f"Parsed JSON data: {data}")
        except Exception as json_error:
            logger.error(f"JSON parsing error: {json_error}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid JSON format", "details": str(json_error)}
            )
        
        user_message = data.get("message", "")
        logger.info(f"User message: {user_message}")
        
        if not user_message.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Message cannot be empty"}
            )
        
        # Check if LLM service is accessible
        logger.info("Calling LLM service...")
        try:
            bot_response = await get_llm_response(user_message)
            logger.info(f"LLM response received: {bot_response[:100]}...")  # Log first 100 chars
        except Exception as llm_error:
            logger.error(f"LLM service error: {llm_error}")
            logger.error(f"LLM error traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"error": "LLM service error", "details": str(llm_error)}
            )
        
        return {"response": bot_response}
        
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "message": "Internal server error", "traceback": traceback.format_exc()}
        )

@app.post("/chat-with-files")
async def chat_with_files(
    message: str = Form(""),
    files: List[UploadFile] = File(...)
):
    try:
        logger.info(f"Received chat-with-files request: message='{message}', files count={len(files)}")
        
        file_contents = []
        file_info = []

        for file in files:
            logger.info(f"Processing file: {file.filename} ({file.content_type})")
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

        logger.info("Calling LLM service with files...")
        try:
            bot_response = await get_llm_response_with_files(message, file_contents)
        except Exception as llm_error:
            logger.error(f"LLM service with files error: {llm_error}")
            logger.error(f"LLM error traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "response": f"Sorry, I encountered an error processing your files: {str(llm_error)}",
                    "error": True
                }
            )

        return {
            "response": bot_response,
            "files_processed": file_info
        }

    except Exception as e:
        logger.error(f"Unexpected error in chat-with-files endpoint: {e}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={
                "response": f"Sorry, I encountered an error processing your files: {str(e)}",
                "error": True,
                "traceback": traceback.format_exc()
            }
        )