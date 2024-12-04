# HomeAssistant-Llama Integration

Combine the power of [Home Assistant](https://www.home-assistant.io/) with Meta’s [Llama 3.2](https://llama.com) to create a private, local, and adaptive smart home assistant. This integration allows you to control smart devices using natural language, ensuring your data stays on your network.

---

## Features

- **Local Processing**: All data is processed locally, ensuring privacy and eliminating cloud dependency.
- **Unified Smart Home Control**: Manage devices across brands via Home Assistant's central hub.
- **User-Friendly Interface**: Interact with the system through a simple Gradio chat interface.

---

## Directory Structure

```plaintext
homeassistant-llama/
|-- backend/
|   |-- agent/
|   |   |-- prompts.py         # Prompts for the Llama model
|   |   |-- services.py        # APIs to interact with Ollama and manage Llama
|   |-- homeassistant/
|   |   |-- functions.py       # APIs to read/control Home Assistant devices
|   |-- ha_config/             # Home Assistant configuration files
|   |-- main.py                # Main FastAPI server logic
|-- frontend/
|   |-- gradio_app.py          # Simple chat UI to interact with the assistant
|-- docker-compose.yaml        # Orchestrates the backend and frontend
```

## Prerequisites:
 
- Docker
- Python 3.10+
- Ollama


## Getting Started

1. Clone the Repository

```bash
git clone https://github.com/miguelg719/homeassistant-llama.git
cd homeassistant-llama
```

2. Set up the backend

Start the backend using docker compose:

```bash
docker compose up --build
```

Configure Home Assistant:
- Visit http://localhost:8123 to complete the onboarding process.
- Generate a Long-Lived Access Token and save it securely.
- Update the .env file in the project root with the token.

3. Run the Frontend

Install Python dependencies:

```bash
pip install gradio requests
```

Run the frontend:

```bash
cd frontend
python gradio_app.py
```

Access the chat interface at http://localhost:7860.

## Usage

You can control smart devices and query the assistant using natural language. Examples:
- Turn on devices: “Turn on the ceiling lights.”
- Adjust settings: “It’s too cold, set the thermostat to 72 degrees.”
- General queries: “What’s the best way to clean a glass stovetop?”

## Contributing

Contributions are welcome! Feel free to:
- Submit issues or feature requests.
- Fork the repository and submit pull requests.

## License

This project is licensed under the MIT License. See the LICENSE file for details.