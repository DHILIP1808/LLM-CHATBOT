import httpx # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from typing import List, Dict, Any

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def get_llm_response(message: str):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": message}],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

async def get_llm_response_with_files(message: str, file_contents: List[Dict[str, Any]]):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build context from files
    file_context = "Here are the uploaded files:\n\n"
    
    for file_data in file_contents:
        filename = file_data["filename"]
        file_type = file_data["type"]
        content = file_data["content"]
        
        file_context += f"**File: {filename}** (Type: {file_type})\n"
        
        if file_type == "text":
            # For text files, include the actual content (truncate if too long)
            if len(content) > 3000:  # Limit content length
                file_context += f"Content (first 3000 characters):\n{content[:3000]}...\n\n"
            else:
                file_context += f"Content:\n{content}\n\n"
        else:
            # For non-text files, just include the description
            file_context += f"{content}\n\n"
    
    # Combine user message with file context
    full_message = f"{file_context}\nUser message: {message}" if message else file_context
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful assistant. The user has uploaded files. Analyze the files and respond to their message accordingly. If they ask questions about the files, refer to the file contents provided."
            },
            {
                "role": "user", 
                "content": full_message
            }
        ],
        "max_tokens": 1500,  # Adjust as needed
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]