import json
import os
from requests import post, get
from pprint import pprint
from dotenv import load_dotenv
from langchain_core.tools import tool
import logging  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

homeassistant_url = os.getenv("HOMEASSISTANT_URL")
token = os.getenv("HOMEASSISTANT_TOKEN")

@tool(parse_docstring=True)
async def turn_light_on(
    entity_id: str,
    brightness_pct: int = -1
):
    """
    A function that takes in a string and turns on a light

    Args:
        entity_id: The name of the light to be turned on. Options are ceiling_lights, bed_light.
        brightness_pct: The brightness level to turn the light on 

    Returns:
        A result string saying successful or unsuccesful command
    """
    logger.info(f"Turning on light {entity_id} with brightness {brightness_pct}")
    url = f"http://{homeassistant_url}:8123/api/services/light/turn_on"
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

    logger.info(f"Sending request to {url} with data: {data}")
    
    try:
        response = post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise exception for bad status codes
        logger.info(f"Light on response status: {response.status_code}")
        logger.info(f"Light on response body: {response.json()}")
        
        if len(response.json()) > 0:
            state = response.json()[0]['state']
            if state == "on":
                return {"state": state, "brightness": str(round(response.json()[0]['attributes']['brightness']/255 * 100))}
            else:
                return {"state": state}
        else:
            return {"state": "not updated"}
            
    except Exception as e:
        logger.error(f"Error turning on light: {str(e)}")
        return {"state": "error", "message": str(e)}

@tool(parse_docstring=True)
async def turn_light_off(
    entity_id: str,
):
    """
    A function that takes in a string and turns off a light

    Args:
        entity_id: The name of the light to be turned off. Options are ceiling_lights, bed_light.

    Returns:
        A json representing the updated state of the light entity
    """
    url = f"http://{homeassistant_url}:8123/api/services/light/turn_off"
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

@tool(parse_docstring=True)
async def turn_climate_on(
    entity_id: str = "hvac",
):
    """
    A function that turns on the default climate entity in the home (or any climate entity specified)

    Args:
        entity_id: The name of the climate system. Option is hvac.

    Returns:
        A json representing the updated state of the climate entity
    """

    url = f"http://{homeassistant_url}:8123/api/services/climate/turn_on"
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

@tool(parse_docstring=True)
async def turn_climate_off(
    entity_id: str = "hvac",
):
    """
    A function that turns off the default climate entity in the home (or specified climate entity)

    Args:
        entity_id: The name of the climate system. Option is hvac.

    Returns:
        A json representing the updated state of the climate entity
    """

    url = f"http://{homeassistant_url}:8123/api/services/climate/turn_off"
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

@tool(parse_docstring=True)
async def set_climate_temperature(
    setpoint: int,
    entity_id: str = "hvac"
):
    """
    A function that adjusts the climate controller setpoint

    Args:
        entity_id: The name of the climate system. Option is hvac.
        setpoint: The temperature to set the climate controller to in degrees Fahrenheit.

    Returns:
        A json representing the updated state of the climate entity
    """

    url = f"http://{homeassistant_url}:8123/api/services/climate/set_temperature"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    data = json.dumps({
        "entity_id": "climate." + entity_id,
        "temperature": setpoint
    })

    response = post(url, headers=headers, data=data)
    # return {"state": response.json()[0]['state']}
    if len(response.json()) > 0:
        return response.json()
    else:
        return {"state": "not updated"}

@tool(parse_docstring=True)
async def set_climate_fan(
    fan_mode: str,
    entity_id: str = "hvac"
):
    """
    A function that adjusts the climate controller fan speed

    Args:
        entity_id: The name of the climate system. Option is hvac.
        fan_mode: The fan speed to set the climate controller to. Options are low, high.

    Returns:
        A json representing the updated state of the climate entity
    """

    url = f"http://{homeassistant_url}:8123/api/services/climate/set_fan_mode"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    # print(fan_mode)
    if fan_mode == "low":
        fan_mode = "on_low"
    elif fan_mode == "high":
        fan_mode = "on_high"
    else:
        fan_mode = "on_low"

    data = json.dumps({
        "entity_id": "climate." + entity_id,
        "fan_mode": fan_mode
    })

    # print(data)
    response = post(url, headers=headers, data=data)
    # print("res", response)
    # return {"state": response.json()[0]['state']}
    if len(response.json()) > 0:
        return response.json()
    else:
        return {"state": "not updated"}

@tool(parse_docstring=True)
async def arm_system(
    entity_id: str,
    code: int, 
    mode: str = 'away'
):
    """
    A function that arms the security system of the home.

    Args:
        entity_id: The name of the security system. Option is security.
        code: The pin code used to arm the home.
        mode: The security mode to arm the home with. Options are home, away, vacation.

    Returns:
        A json representing the updated state of the security entity
    """

    url = f'http://{homeassistant_url}:8123/api/services/alarm_control_panel/alarm_arm_{mode}'
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    data = json.dumps({
        "entity_id": "alarm_control_panel." + entity_id,
        "code": code
    })

    # print(data)
    response = post(url, headers=headers, data=data)
    print("res", response.json())
    # return {"state": response.json()[0]['state']}
    if len(response.json()) > 0:
        return response.json()
    else:
        return {"state": "not updated"}

@tool(parse_docstring=True)
async def disarm_system(
    entity_id: str,
    code: int, 
):
    """
    A function that disarms the security system of the home.

    Args:
        entity_id: The name of the security system. Option is security.
        code: The pin code used to disarm the home.

    Returns:
        A json representing the updated state of the security entity
    """

    url = f'http://{homeassistant_url}:8123/api/services/alarm_control_panel/alarm_disarm'
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    data = json.dumps({
        "entity_id": "alarm_control_panel." + entity_id,
        "code": code
    })

    # print(data)
    response = post(url, headers=headers, data=data)
    print("res", response)
    # return {"state": response.json()[0]['state']}
    if len(response.json()) > 0:
        return response.json()
    else:
        return {"state": "not updated"}

@tool(parse_docstring=True)
async def get_light_state(
    entity_id: str
):
    """
    A function to get the state of a specific light.

    Args:
        entity_id: The name of the light. Option is ceiling_lights, bed_light.

    Returns:
        A json representing the state of the light entity
    """

    url = f'http://{homeassistant_url}:8123/api/states/light.{entity_id}'
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    # print(url)
    response = get(url, headers=headers)
    pprint(response.json())
    return response.json()

@tool(parse_docstring=True)
async def get_climate_state(
    entity_id: str
):
    """
    A function to get the state of a climate entity.

    Args:
        entity_id: The name of the climate entity. Option is hvac.

    Returns:
        A json representing the state of the climate entity
    """

    url = f'http://{homeassistant_url}:8123/api/states/climate.{entity_id}'
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    # print(url)
    response = get(url, headers=headers)
    pprint(response.json())
    return response.json()

@tool(parse_docstring=True)
async def get_security_state(
    entity_id: str
):
    """
    A function to get the state of a security entity.

    Args:
        entity_id: The name of the security entity. Option is security.

    Returns:
        A json representing the state of the security entity
    """
    url = f'http://{homeassistant_url}:8123/api/states/alarm_control_panel.{entity_id}'
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }
    # print(url)
    response = get(url, headers=headers)
    pprint(response.json())
    return response.json()


tools = [turn_light_on, turn_light_off, turn_climate_on, turn_climate_off, set_climate_temperature, set_climate_fan, arm_system, disarm_system, get_light_state, get_climate_state, get_security_state]