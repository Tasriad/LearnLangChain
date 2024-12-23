from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("MISTRAL_API_KEY"):
    from getpass import getpass
    os.environ["MISTRAL_API_KEY"] = getpass("Enter API key for Mistral AI: ")
    
messages = [
    SystemMessage(content="You are an expert in anime"),
    HumanMessage(content="Suggest me some good animes to watch shortly highlighting the genre, plot."),
]

from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model="mistral-large-latest")

response = model.invoke(messages)
print(response.content)
