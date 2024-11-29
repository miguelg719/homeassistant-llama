import gradio as gr
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKEND_URL = "http://localhost:8000"

def chat_with_agent(message, history):
    if history is None:
        history = []
    
    try:
        # Prepare the request
        payload = {
            "prompt": message,
            "previous_context": history[-1][1] if history else None
        }
        
        logger.info(f"Sending request with payload: {payload}")
        
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        logger.info(f"Raw response from backend: {result}")
        
        # Extract the actual response text
        if isinstance(result, dict) and "response" in result:
            response_data = result["response"]
            if isinstance(response_data, dict):
                assistant_message = response_data.get("response", str(response_data))
            else:
                assistant_message = str(response_data)
        else:
            assistant_message = str(result)
            
        logger.info(f"Final assistant message: {assistant_message}")
        
        # Update history with the new message pair
        new_history = history + [[message, assistant_message]]
        
        return "", new_history

    except Exception as e:
        logger.error(f"Error in chat_with_agent: {str(e)}", exc_info=True)
        return "", history + [[message, f"Error: {str(e)}"]]

# Create Gradio interface
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(
        label="Chat with Llama",
        height=600,
        show_copy_button=True,
    )
    
    with gr.Row():
        msg = gr.Textbox(
            show_label=False,
            placeholder="Type your message here...",
            container=False,
            scale=7
        )
        submit = gr.Button("Send", scale=1)
        clear = gr.Button("Clear", scale=1)

    # Event handlers
    msg.submit(
        chat_with_agent,
        [msg, chatbot],
        [msg, chatbot]
    )
    
    submit.click(
        chat_with_agent,
        [msg, chatbot],
        [msg, chatbot]
    )
    
    clear.click(
        lambda: (None, []),
        None,
        [msg, chatbot],
        queue=False
    )

if __name__ == "__main__":
    demo.launch(share=False)