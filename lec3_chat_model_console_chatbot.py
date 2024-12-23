from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("MISTRAL_API_KEY"):
    from getpass import getpass
    os.environ["MISTRAL_API_KEY"] = getpass("Enter API key for Mistral AI: ")

messages = [
    SystemMessage(content="You are an expert in anime")
]

from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model="mistral-large-latest")

print("Chat with the AI (type 'quit' to exit)")
while True:
    user_input = input("You: ")
    if user_input.lower() == 'quit':
        break
        
    messages.append(HumanMessage(content=user_input))
    response = model.invoke(messages)
    print("AI:", response.content)
    messages.append(AIMessage(content=response.content))
