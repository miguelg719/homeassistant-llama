from llama_stack_client import LlamaStackClient
from llama_stack_client.lib.agents.agent import Agent
from llama_stack_client.types.agent_create_params import AgentConfig
from llama_stack_client.lib.agents.event_logger import EventLogger
from llama_stack_client.types import CompletionMessage, ToolResponseMessage
from ..homeassistant.functions import (
    ExampleTool, LightTurnOnTool, LightTurnOffTool,
    ClimateTurnOnTool, ClimateTurnOffTool, SetClimateTemperatureTool,
    SetClimateFanTool, ArmSystemTool, DisarmSystemTool
)
from pprint import pprint

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_llama_agent(system_message):
    client = LlamaStackClient(base_url=f"http://localhost:5001")
    
    available_models = [model.identifier for model in client.models.list()]
    if not available_models:
        raise ValueError("No available models")
    selected_model = available_models[0]
    logger.info(f"Using model: {selected_model}")

    agent_config = AgentConfig(
        model=selected_model,
        instructions=system_message,
        sampling_params={
            "strategy": "greedy",
            "temperature": 0.0,
            "top_p": 0.9,
        },
        tools=(
            [
                {
                  "type": "function_call",
                  "description": "A tool that takes a single message and prints it",
                  "function_name": "example_tool",
                  "parameters": {
                      "message": {
                          "param_type": "str",
                          "description": "The message to be processed by the tool",
                          "required": True,
                      }
                   }
                },
                {
                  "type": "function_call",
                  "description": "A tool that turns on a light with specific brightness",
                  "function_name": "light_turn_on",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The light id to turn on",
                          "required": True,
                      },
                      "brightness_pct": {
                          "param_type": "int",
                          "description": "The brightness level to turn the light on",
                          "required": False,
                      }
                   }
                },
                {
                  "type": "function_call",
                  "description": "A tool that turns off a light",
                  "function_name": "light_turn_off",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The light id to turn off",
                          "required": True,
                      }
                   }
                },
                {
                  "type": "function_call",
                  "description": "A tool that turns on a climate entity",
                  "function_name": "climate_turn_on",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the climate system (hvac). Use 'hvac'",
                          "required": False,
                      },
                      "mode": {
                          "param_type": "str",
                          "description": "The mode to turn the climate on (auto, cool, heat)",
                          "required": False,
                      }
                  }
                },
                {
                  "type": "function_call",
                  "description": "A tool that turns off a climate entity",
                  "function_name": "climate_turn_off",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the climate system (default: hvac)",
                          "required": False,
                      }
                  }
                },
                {
                  "type": "function_call",
                  "description": "A tool that adjusts the climate controller setpoint",
                  "function_name": "set_climate_temperature",
                  "parameters": {
                      "setpoint": {
                          "param_type": "int",
                          "description": "The temperature to set in degrees Fahrenheit",
                          "required": True,
                      },
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the climate system (default: hvac)",
                          "required": False,
                      }
                  }
                },
                {
                  "type": "function_call",
                  "description": "A tool that adjusts the climate controller fan speed",
                  "function_name": "set_climate_fan",
                  "parameters": {
                      "fan_mode": {
                          "param_type": "str",
                          "description": "The fan speed (low, high)",
                          "required": True,
                      },
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the climate system (default: hvac)",
                          "required": False,
                      }
                  }
                },
                {
                  "type": "function_call",
                  "description": "A tool that arms the security system of the home",
                  "function_name": "arm_system",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the security system (security)",
                          "required": True,
                      },
                      "code": {
                          "param_type": "int",
                          "description": "The pin code used to arm the home",
                          "required": True,
                      },
                      "mode": {
                          "param_type": "str",
                          "description": "The security mode (home, away, vacation)",
                          "required": False,
                      }
                  }
                },
                {
                  "type": "function_call",
                  "description": "A tool that disarms the security system of the home",
                  "function_name": "disarm_system",
                  "parameters": {
                      "entity_id": {
                          "param_type": "str",
                          "description": "The name of the security system (security)",
                          "required": True,
                      },
                      "code": {
                          "param_type": "int",
                          "description": "The pin code used to disarm the home",
                          "required": True,
                      }
                  }
                }
            ]
        ),
        
        tool_choice="auto",
        tool_prompt_format="python_list",
        input_shields=[],
        output_shields=[],
        enable_session_persistence=False,
    )

    agent = Agent(client, agent_config, custom_tools=[
        ExampleTool(), 
        LightTurnOnTool(), 
        LightTurnOffTool(),
        ClimateTurnOnTool(),
        ClimateTurnOffTool(),
        SetClimateTemperatureTool(),
        SetClimateFanTool(),
        ArmSystemTool(),
        DisarmSystemTool(),
    ])
    
    return agent

# TODO: Enable previous context for mem
async def ollama_chat_completion(system_message, user_message, previous_context=None):
    try:
        agent = await create_llama_agent(system_message)
        session_id = agent.create_session("user-session")

        messages = [
            {
                'content': user_message,
                'role': 'user'
            },
            {
                'content': 'Explain to the user if you achieved your goal, ask if they need anything else. Be extremely concise.',
                'role': 'user'
            }
        ]

        # TODO: Try system prompt? 
        res = None
        for message in messages:
            response = agent.create_turn(
                messages=[message],
                session_id=session_id,
            )

            # for log in EventLogger().log(response):
            #     log.print() 
            for r in response:
                if hasattr(r, 'event') and hasattr(r.event, 'payload'):
                        if r.event.payload.event_type == 'turn_complete':
                            turn_res = r.event.payload.turn
                            print(turn_res)
                            if hasattr(turn_res, 'output_message'):
                                res =  turn_res.output_message.content
        
        return res

    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
        raise

