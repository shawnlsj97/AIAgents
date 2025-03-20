import ollama
import time

# Define the debate setup
AGENT_1_ROLE = "A philosopher who strongly argues for the existence of God. Your goal is to convince your opponent that God exists using logic, philosophy, and evidence."
AGENT_2_ROLE = "A skeptical scientist who strongly argues against the existence of God. Your goal is to refute your opponent's arguments and prove that God does not exist."

# Initialize messages with system prompt
messages = [
    {"role": "system", "content": "Two AI agents will debate furiously over the existence of God. They will take turns presenting arguments and counterarguments. Please include anger in the argument."},
]

# Define agent identities
agent_1 = {"role": "assistant", "name": "Philosopher", "persona": AGENT_1_ROLE}
agent_2 = {"role": "assistant", "name": "Scientist", "persona": AGENT_2_ROLE}

# Number of debate rounds
rounds = 5

# Start the debate with the philosopher's opening argument
current_speaker = agent_1  

for i in range(rounds):
    print(f"\n🔹 ROUND {i+1}: {current_speaker['name']} speaks 🔹\n")

    # Add the current speaker's persona to guide the response
    messages.append({"role": "system", "content": current_speaker["persona"]})

    # Get response from Ollama
    stream = ollama.chat(
        model="llama3.1",
        messages=messages,
        stream=True  # Enable streaming for real-time output
    )

    # Display response in real-time
    response_content = ""
    for chunk in stream:
        text = chunk["message"]["content"]
        response_content += text
        print(text, end="", flush=True)
        time.sleep(0.02)  # Simulate real-time "thinking"

    print("\n" + "-" * 80)

    # Add response to chat history
    messages.append({"role": "assistant", "content": response_content})

    # Switch turns between the Philosopher and Scientist
    current_speaker = agent_2 if current_speaker == agent_1 else agent_1
