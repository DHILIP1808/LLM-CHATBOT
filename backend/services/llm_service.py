import httpx # type: ignore
import os
from dotenv import load_dotenv # type: ignore
from typing import List, Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Log API key status (without exposing the actual key)
logger.info(f"OpenRouter API Key loaded: {bool(OPENROUTER_API_KEY)}")
if OPENROUTER_API_KEY:
    logger.info(f"API Key length: {len(OPENROUTER_API_KEY)}")
    logger.info(f"API Key starts with: {OPENROUTER_API_KEY[:8]}...")

async def get_llm_response(message: str):
    try:
        # Validate inputs
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        if not message.strip():
            raise ValueError("Message cannot be empty")
        
        logger.info(f"Sending message to OpenRouter: {message[:100]}...")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1000,  # Add max_tokens to prevent issues
            "temperature": 0.7   # Add temperature for consistency
        }
        
        logger.info(f"Request payload: {payload}")
        
        # Set timeout to prevent hanging
        timeout = httpx.Timeout(30.0, connect=10.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")
                
                # Check if request was successful
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenRouter API error: Status {response.status_code}, Response: {error_text}")
                    raise httpx.HTTPStatusError(
                        f"OpenRouter API returned {response.status_code}: {error_text}",
                        request=response.request,
                        response=response
                    )
                
                data = response.json()
                logger.info(f"Response data keys: {list(data.keys())}")
                
                # Validate response structure
                if "choices" not in data:
                    logger.error(f"Invalid response structure: {data}")
                    raise ValueError(f"Invalid response from OpenRouter API: {data}")
                
                if not data["choices"] or len(data["choices"]) == 0:
                    logger.error(f"No choices in response: {data}")
                    raise ValueError("No response choices received from OpenRouter API")
                
                if "message" not in data["choices"][0]:
                    logger.error(f"No message in choice: {data['choices'][0]}")
                    raise ValueError("No message in response choice")
                
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Successfully received response: {content[:100]}...")
                return content
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during API call: {e}")
                raise
            except httpx.TimeoutException as e:
                logger.error(f"Timeout during API call: {e}")
                raise ValueError("Request to OpenRouter API timed out")
            except Exception as e:
                logger.error(f"Unexpected error during API call: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Error in get_llm_response: {e}")
        raise

async def get_llm_response_with_files(message: str, file_contents: List[Dict[str, Any]]):
    try:
        # Validate inputs
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        
        logger.info(f"Processing files: {len(file_contents)} files, message: {message[:100] if message else 'No message'}...")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # Build context from files
        file_context = "Here are the uploaded files:\n\n"
        
        for file_data in file_contents:
            filename = file_data.get("filename", "unknown")
            file_type = file_data.get("type", "unknown")
            content = file_data.get("content", "")
            
            file_context += f"**File: {filename}** (Type: {file_type})\n"
            
            if file_type == "text":
                # For text files, include the actual content (truncate if too long)
                if len(str(content)) > 3000:  # Limit content length
                    file_context += f"Content (first 3000 characters):\n{str(content)[:3000]}...\n\n"
                else:
                    file_context += f"Content:\n{str(content)}\n\n"
            else:
                # For non-text files, just include the description
                file_context += f"{str(content)}\n\n"
        
        # Combine user message with file context
        full_message = f"{file_context}\nUser message: {message}" if message else file_context
        
        # Truncate if the full message is too long (OpenRouter has token limits)
        if len(full_message) > 10000:  # Rough character limit
            full_message = full_message[:10000] + "\n\n[Message truncated due to length]"
        
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
            "max_tokens": 1500,
            "temperature": 0.7
        }
        
        logger.info(f"Request payload prepared with {len(payload['messages'])} messages")
        
        # Set timeout to prevent hanging
        timeout = httpx.Timeout(60.0, connect=10.0)  # Longer timeout for file processing
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
                logger.info(f"Response status code: {response.status_code}")
                
                # Check if request was successful
                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"OpenRouter API error: Status {response.status_code}, Response: {error_text}")
                    raise httpx.HTTPStatusError(
                        f"OpenRouter API returned {response.status_code}: {error_text}",
                        request=response.request,
                        response=response
                    )
                
                data = response.json()
                
                # Validate response structure
                if "choices" not in data or not data["choices"]:
                    logger.error(f"Invalid response structure: {data}")
                    raise ValueError(f"Invalid response from OpenRouter API: {data}")
                
                content = data["choices"][0]["message"]["content"]
                logger.info(f"Successfully received file response: {content[:100]}...")
                return content
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error during API call with files: {e}")
                raise
            except httpx.TimeoutException as e:
                logger.error(f"Timeout during API call with files: {e}")
                raise ValueError("Request to OpenRouter API timed out")
            except Exception as e:
                logger.error(f"Unexpected error during API call with files: {e}")
                raise
                
    except Exception as e:
        logger.error(f"Error in get_llm_response_with_files: {e}")
        raise