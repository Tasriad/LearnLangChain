import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if the API key is set; otherwise, prompt for it
if not os.getenv("MISTRAL_API_KEY"):
    from getpass import getpass
    os.environ["MISTRAL_API_KEY"] = getpass("Enter API key for Mistral AI: ")

# Import and initialize the ChatMistralAI model
from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model="mistral-large-latest")

# Example invocation
response = model.invoke("Do you know what anime is?")
print(response.content)