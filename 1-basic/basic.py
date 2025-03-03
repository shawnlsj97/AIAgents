from ollama import chat, ChatResponse

response: ChatResponse = chat(
    model="llama3.1", 
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
)
print(response.message.content)

stream = chat(
    model="llama3.1", 
    messages=[
        {
            "role": "user",
            "content": "Why is the sky blue?",
        },
    ],
    stream=True
)
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)