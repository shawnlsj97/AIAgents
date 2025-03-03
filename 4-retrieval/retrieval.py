import json
from ollama import chat, ChatResponse
from pydantic import BaseModel, Field

# Define knowledge base retrieval tool
def search_kb(question: str):
    """
    Load the whole knowledge base from the JSON file.
    (This is a mock function for demonstration purposes, we don't search)
    """
    with open("kb.json", "r") as f:
        return json.load(f)

# Call model with tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "Get the answer to the user's question from the knowledge base.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

system_prompt = "You are a helpful assistant that answers questions from the knowledge base about our e-commerce store."

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the return policy?"},
]

# Model makes decision whether to call function
response: ChatResponse = chat(
    model="llama3.1",
    messages=messages,
    tools=tools,
)

print(response.model_dump())

# Get args returned from model to call function
available_functions = {
    "search_kb": search_kb,
}

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

# Supply result to model to get it in desired format
class KBResponse(BaseModel):
    answer: str = Field(description="The answer to the user's question.")
    source: int = Field(description="The record id of the answer.")

response: ChatResponse = chat(
    model="llama3.1",
    messages=messages,
    tools = tools,
    format=KBResponse.model_json_schema(),
)

print("Final response:", response.message.content)
kb_response = KBResponse.model_validate_json(response.message.content) # create object
print(kb_response.answer)
print(kb_response.source)

# Example of question that does not trigger tool
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "What is the weather in Tokyo?"},
]

response: ChatResponse = chat(
    model="llama3.1",
    messages=messages,
    tools = tools,
)
print("No tool response:", response.message.content)