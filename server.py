from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from brt_llm import brt_bot
from brt_mongo import save_chat, clear_chat_history 
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    if not message.message:
        raise HTTPException(status_code=400, detail="No message provided")
    
    user_id = "harisjamal&rahimshah"

    save_chat(user_id, "user", message.message)

    response = brt_bot(message.message, user_id)

    if not response:
        response = "Sorry, I couldn't understand your request. Please try again."

    save_chat(user_id, "assistant", response)

    return ChatResponse(response=response)

@app.post("/chat/clear")
async def clear_chat():
    clear_chat_history()
    return {"message": "Chat history cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)