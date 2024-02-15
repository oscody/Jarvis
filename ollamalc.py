# Testing Ollama running locally
# With Ollama serve
# Need to also run ollama pull $modelName in other terminal 
# pip install langchain-community

from langchain_community.llms import Ollama

model = "tinyllama"

llm = Ollama(model=model)

question = "Answer in 1 sentence or less what is the capital of Jamaica the Island if you dont know the answer say idk?"

response = llm.invoke(question)

print(f"response is {response}")