from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Specify local LLM
local_llm = "llama3.1"

# Initialize ChatOllama model with desired parameters
llm = OllamaLLM(model=local_llm, temperature=0)

# Define prompt template
template = "Question: {question}\nAnswer: Let's think step by step."
prompt = ChatPromptTemplate.from_template(template)

# Craft specific prompt
formatted_prompt = prompt.format(question="Why do programmers always say Hello World?")

# Define langchain
llm_chain = prompt | llm
generation = llm_chain.invoke(formatted_prompt)
print(generation)