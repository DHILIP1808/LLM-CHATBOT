from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from services.llm_service import get_llm_response

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
