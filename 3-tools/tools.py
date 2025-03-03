import requests
import json
from ollama import chat, ChatResponse
from pydantic import BaseModel, Field

"""
reference: https://ollama.com/blog/tool-support
"""


# Step 1: Define tools (functions) that we want to call
def get_weather(latitude, longitude):
    """This is a publically available API that returns the weather for a given location."""
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]

# Define tools for model to use
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

messages = [
    { 
        "role": "system", 
        "content": "You are a helpful weather assistant.",
    },
    {
        "role": "user",
        "content": "What's the weather like in Paris today?",
    },
]

# Step 2: Model determines whether to call functions
response: ChatResponse = chat(
    model="llama3.1",
    messages=messages,
    tools=tools,
)

print(response.model_dump())

available_functions = {
    "get_weather": get_weather,
}

# Step 3: Use args returned by model to perform actual function calls
if response.message.tool_calls:
    for tool in response.message.tool_calls: # multiple tools may be called in 1 response
        if function_to_call := available_functions.get(tool.function.name):
            """
            ":=" is called walrus operator (introduced in Python 3.8). Allows assignment as part of an expression.
            Equivalent code without ":=" :
                function_to_call = available_functions.get(tool.function.name)
                if function_to_call:
            """
            print('Calling function:', tool.function.name)
            print('Arguments:', tool.function.arguments)
            output = function_to_call(**tool.function.arguments) # ** used for dictionary unpacking
            print('Function output:', output)
            messages.append(
                {"role": "tool", "tool_call_name": tool.function.name, "content": json.dumps(output)}
            )
        else:
            print('Function', tool.function.name, 'not found')
 
# Step 4: Supply model with result to get it in format that we want
class WeatherResponse(BaseModel):
    temperature: float = Field(
        description="The current temperature in celsius for the given location."
    )
    response: str = Field(
        description="A natural language response to the user's question."
    )

response: ChatResponse = chat(
    model="llama3.1",
    messages=messages,
    tools = tools,
    format=WeatherResponse.model_json_schema(),
)

print("Final response:", response.message.content)
weather = WeatherResponse.model_validate_json(response.message.content) # create object
print(weather.temperature)
print(weather.response)
