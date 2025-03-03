from ollama import chat
from pydantic import BaseModel

# Define response format in a Pydantic model
class CalendarEvent(BaseModel):
    name: str
    date: str
    participants: list[str]

response = chat(
    model="llama3.1",
    messages=[
        { 
            "role": "system", 
            "content": "Extract the event information",
        },
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on Friday",
        }
    ],
    format=CalendarEvent.model_json_schema(),
)

event = CalendarEvent.model_validate_json(response.message.content)
print(event)
print(event.name)
print(event.date)
print(event.participants)