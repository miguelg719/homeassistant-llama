import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from .agent.services import ollama_chat_completion
from pydantic import BaseModel
from fastapi import HTTPException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

class ChatInput(BaseModel):
    prompt: str
    previous_context: str | None = None

async def get_answer(prompt, previous_context=None):
    try:
        response = await ollama_chat_completion(
            system_message="You are a helpful assistant that can control home automation devices. Respond after the tool call is made.",
            user_message=prompt, 
            previous_context=previous_context
        )
        
        logger.info(f"Llama response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error in get_answer: {str(e)}", exc_info=True)
        raise

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-ollama")
async def test_ollama():
    try:
        response = await ollama_chat_completion(
            system_message="You are a helpful assistant.",
            user_message="Hello, are you working?"
        )
        return {"success": True, "response": response}
    except Exception as e:
        logger.error(f"Error testing Ollama: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ollama test failed: {str(e)}"
        )

@app.post("/chat")
async def chat_endpoint(chat_input: ChatInput):
    try:
        response = await get_answer(chat_input.prompt, chat_input.previous_context)
        if response:
            return {"success": True, "response": response[1:-1]}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)