import json
from abc import abstractmethod
from typing import List

from llama_stack_client.lib.agents.custom_tool import CustomTool
from llama_stack_client.types import CompletionMessage, ToolResponseMessage
from typing import Dict
from llama_stack_client.types.tool_param_definition_param import ToolParamDefinitionParam
from dotenv import load_dotenv
from requests import post, get
import os

load_dotenv()

# homeassistant_url = os.getenv("HOMEASSISTANT_URL")
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwZmI4NWJjN2IxYzE0MDljOWJjNWJiYTU2MTYyNWY4MSIsImlhdCI6MTczMjk0NTI5MiwiZXhwIjoyMDQ4MzA1MjkyfQ.EaDuNxRYPnkcEBJYdMG7XMYdmO1kD0hQ0DWXIWjDa3Q'
print(f"token: {token}")

class SingleMessageCustomTool(CustomTool):
    """
    Helper class to handle custom tools that take a single message
    Extending this class and implementing the `run_impl` method will
    allow for the tool be called by the model and the necessary plumbing.
    """

    def run(self, messages: List[CompletionMessage]) -> List[ToolResponseMessage]:
        assert len(messages) == 1, "Expected single message"

        message = messages[0]

        tool_call = message.tool_calls[0]
        print(f"\n\n\nmessage: {message}, tool_call: {tool_call}")

        try:
            response = self.run_impl(**tool_call.arguments)
            response_str = json.dumps(response, ensure_ascii=False)
        except Exception as e:
            response_str = f"Error when running tool: {e}"

        message = ToolResponseMessage(
            call_id=tool_call.call_id,
            tool_name=tool_call.tool_name,
            content=response_str,
            role="ipython",
        )
        return [message]

    @abstractmethod
    def run_impl(self, *args, **kwargs):
        raise NotImplementedError()

class ExampleTool(SingleMessageCustomTool):
    """
    Helper class to handle custom tools that take a single message
    Extending this class and implementing the `run_impl` method will
    allow for the tool be called by the model and the necessary plumbing.
    """

    def get_name(self) -> str:
        return "example_tool"

    def get_description(self) -> str:
        return "prints the message"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "message": ToolParamDefinitionParam(
                param_type="str",
                description="The message to be processed by the tool",
                required=True,
            )
        }

    
    def run_impl(self, *args, **kwargs):
        print(f"\n\n\nRunning tool with args: {args} and kwargs: {kwargs}")
        return f"Message received: {kwargs['message']}"
    

  

class LightTurnOnTool(SingleMessageCustomTool):

    def get_name(self) -> str:
        return "light_turn_on"

    def get_description(self) -> str:
        return "Turn on a light with specific brightness"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The entity id of the light to be turned on",
                required=True,
            ),
            "brightness_pct": ToolParamDefinitionParam(
                param_type="int",
                description="The brightness level to turn the light on",
                required=False,
            )
        }

    
    def run_impl(self, *args, **kwargs):
      entity_id = kwargs['entity_id']
      brightness_pct = kwargs['brightness_pct']
      url = f"http://localhost:8123/api/services/light/turn_on"
      headers = {
          "Authorization": f"Bearer {token}",
          "content-type": "application/json",
      }

      # Initialize data with base configuration
      data = json.dumps({
          "entity_id": "light." + entity_id
      })

      # Add brightness only if valid value provided
      if brightness_pct >= 0 and brightness_pct <= 100:
          data = json.dumps({
              "entity_id": "light." + entity_id,
              "brightness_pct": brightness_pct
          })

      
      try:
          response = post(url, headers=headers, data=data)
          response.raise_for_status()  # Raise exception for bad status codes
          print(f"Light on response status: {response.status_code}")
          print(f"Light on response body: {response.json()}")
          
          if len(response.json()) > 0:
              state = response.json()[0]['state']
              if state == "on":
                  return {"state": state, "brightness": str(round(response.json()[0]['attributes']['brightness']/255 * 100))}
              else:
                  return {"state": state}
          else:
              return {"state": "not updated"}
              
      except Exception as e:
          print(f"Error turning on light: {str(e)}")
          return {"state": "error", "message": str(e)}
      



class LightTurnOffTool(SingleMessageCustomTool):

    def get_name(self) -> str:
        return "light_turn_off"

    def get_description(self) -> str:
        return "Turn on a light with specific brightness"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The entity id of the light to be turned on",
                required=True,
            ),
            "brightness_pct": ToolParamDefinitionParam(
                param_type="int",
                description="The brightness level to turn the light on",
                required=False,
            )
        }

    
    def run_impl(self, *args, **kwargs):
      entity_id = kwargs['entity_id']
      url = f"http://localhost:8123/api/services/light/turn_off"
      headers = {
          "Authorization": f"Bearer {token}",
          "content-type": "application/json",
      }
      data = json.dumps({
          "entity_id": "light."+entity_id
      })

      response = post(url, headers=headers, data=data)
      # print(response.text)

      # logger.info(reason, extra={"title": "Shutting down...\n"})
      if len(response.json()) > 0:
          # print(response.json()[0]['state'], response.json()[0]['attributes']['brightness'])
          return {"state": response.json()[0]['state']}
      else:
          return {"state": "not updated"}

class ClimateTurnOnTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "climate_turn_on"

    def get_description(self) -> str:
        return "Turn on a climate entity"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the climate system (default: hvac)",
                required=False,
            ),
            "mode": ToolParamDefinitionParam(
                param_type="str",
                description="The mode to turn the climate on (auto, cool, heat)",
                required=True,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs.get('entity_id', 'hvac')
        mode = kwargs.get('mode', 'auto')
        url = f"http://localhost:8123/api/services/climate/set_hvac_mode"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "climate." + entity_id,
            "hvac_mode": mode
        })

        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return {"state": response.json()[0]['state']}
        else:
            return {"state": "not updated"}

class ClimateTurnOffTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "climate_turn_off"

    def get_description(self) -> str:
        return "Turn off a climate entity"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the climate system (default: hvac)",
                required=False,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs.get('entity_id', 'hvac')
        url = f"http://localhost:8123/api/services/climate/turn_off"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "climate." + entity_id
        })

        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return {"state": response.json()[0]['state']}
        else:
            return {"state": "not updated"}

class SetClimateTemperatureTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "set_climate_temperature"

    def get_description(self) -> str:
        return "Adjust the climate controller setpoint"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "setpoint": ToolParamDefinitionParam(
                param_type="int",
                description="The temperature to set in degrees Fahrenheit",
                required=True,
            ),
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the climate system (default: hvac)",
                required=False,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs.get('entity_id', 'hvac')
        setpoint = kwargs['setpoint']
        url = f"http://localhost:8123/api/services/climate/set_temperature"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "climate." + entity_id,
            "temperature": setpoint
        })

        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return response.json()
        else:
            return {"state": "not updated"}

class SetClimateFanTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "set_climate_fan"

    def get_description(self) -> str:
        return "Adjust the climate controller fan speed"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "fan_mode": ToolParamDefinitionParam(
                param_type="str",
                description="The fan speed (low, high)",
                required=True,
            ),
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the climate system (default: hvac)",
                required=False,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs.get('entity_id', 'hvac')
        fan_mode = kwargs['fan_mode']
        
        if fan_mode == "low":
            fan_mode = "on_low"
        elif fan_mode == "high":
            fan_mode = "on_high"
        else:
            fan_mode = "on_low"

        url = f"http://localhost:8123/api/services/climate/set_fan_mode"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "climate." + entity_id,
            "fan_mode": fan_mode
        })

        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return response.json()
        else:
            return {"state": "not updated"}

class ArmSystemTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "arm_system"

    def get_description(self) -> str:
        return "Arm the security system of the home"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the security system (security)",
                required=True,
            ),
            "code": ToolParamDefinitionParam(
                param_type="int",
                description="The pin code used to arm the home",
                required=True,
            ),
            "mode": ToolParamDefinitionParam(
                param_type="str",
                description="The security mode (home, away, vacation)",
                required=False,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs['entity_id']
        code = int(kwargs['code'])
        mode = kwargs.get('mode', 'away')
        
        url = f"http://localhost:8123/api/services/alarm_control_panel/alarm_arm_{mode}"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "alarm_control_panel." + entity_id,
            "code": code
        })

        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return response.json()
        else:
            return {"state": "not updated"}

class DisarmSystemTool(SingleMessageCustomTool):
    def get_name(self) -> str:
        return "disarm_system"

    def get_description(self) -> str:
        return "Disarm the security system of the home"

    def get_params_definition(self) -> Dict[str, ToolParamDefinitionParam]:
        return {
            "entity_id": ToolParamDefinitionParam(
                param_type="str",
                description="The name of the security system (security)",
                required=True,
            ),
            "code": ToolParamDefinitionParam(
                param_type="int",
                description="The pin code used to disarm the home",
                required=True,
            )
        }
    
    def run_impl(self, *args, **kwargs):
        entity_id = kwargs['entity_id']
        code = int(kwargs['code'])
        
        url = f"http://localhost:8123/api/services/alarm_control_panel/alarm_disarm"
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        data = json.dumps({
            "entity_id": "alarm_control_panel." + entity_id,
            "code": code
        })
        print(data)
        response = post(url, headers=headers, data=data)
        if len(response.json()) > 0:
            return response.json()
        else:
            return {"state": "not updated"}
