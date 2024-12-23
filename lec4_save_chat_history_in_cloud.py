"""
This script is a simple chat application that allows you to interact with an AI model. It saves the chat history to a Supabase database.
So first we need to create a supabase account and create a new project.
Then we need to create a new database and a new table called "messages" with the following columns:
- id: default
- conversation_id: same as id
- role: text
- content: text
- created_at: timestamp

Then we need to create a new table called "conversations" with the following columns:
- id: default
- title: text
- created_at: timestamp

Then we need to setup foregin key relationship between the "messages" table and the "conversations" table by the column "conversation_id".

we also need to disable the row level security in the supabase dashboard. We can just got RLS option from each table and disable it.
"""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage  # Import relevant classes from langchain_core for message handling
import os  # Import the os library for environment variable management
from dotenv import load_dotenv  # Import load_dotenv to load environment variables from a .env file
from supabase import create_client  # Import the Supabase client to interact with the Supabase database
from datetime import datetime  # Import datetime to handle timestamps for saving messages

# Load environment variables from a .env file
load_dotenv()

# Check if the MISTRAL_API_KEY is already set in the environment. If not, prompt the user to enter it.
if not os.getenv("MISTRAL_API_KEY"):
    from getpass import getpass  # Import getpass for securely entering the API key
    os.environ["MISTRAL_API_KEY"] = getpass("Enter API key for Mistral AI: ")  # Store the API key in the environment variable

# Initialize the Supabase client using the URL and key from environment variables
supabase_url = os.getenv("SUPABASE_URL")  # Get the Supabase URL from environment variables
supabase_key = os.getenv("SUPABASE_KEY")  # Get the Supabase key from environment variables
supabase = create_client(supabase_url, supabase_key)  # Create a Supabase client instance

# Create a new conversation entry or fetch an existing one from Supabase
conversation_title = 'Anime Expert Chat'  # The title of the conversation
# Fetch conversation data from the 'conversations' table where the title matches
conversation_data = supabase.table('conversations').select('*').eq('title', conversation_title).execute().data

# If no conversation exists, create a new conversation entry in the 'conversations' table
if len(conversation_data) == 0:
    # Insert a new conversation with the current timestamp and title
    conversation_id = supabase.table('conversations').insert({
        'created_at': datetime.now().isoformat(),  # Set the current time as the creation timestamp
        'title': conversation_title  # Set the title of the conversation
    }).execute().data[0]['id']  # Get the ID of the newly created conversation
else:
    # If the conversation already exists, use its ID
    conversation_id = conversation_data[0]['id']

# Initialize the list of messages for the conversation, starting with a SystemMessage
messages = [SystemMessage(content="You are an expert in anime")]  # SystemMessage sets the context for the conversation

# Fetch previous messages from the 'messages' table for the current conversation
previous_messages = supabase.table('messages').select('*').eq('conversation_id', conversation_id).order('created_at').execute().data

# Loop through each previous message and append it to the 'messages' list
for msg in previous_messages:
    # If the message is from the user, append it as a HumanMessage
    if msg['role'] == 'user':
        messages.append(HumanMessage(content=msg['content']))
    # If the message is from the assistant, append it as an AIMessage
    elif msg['role'] == 'assistant':
        messages.append(AIMessage(content=msg['content']))

# Import the Mistral AI model from langchain_mistralai
from langchain_mistralai import ChatMistralAI

# Initialize the Mistral AI model with the "mistral-large-latest" model
model = ChatMistralAI(model="mistral-large-latest")

# Start the conversation loop with a prompt for the user to type
print("Chat with the AI (type 'quit' to exit)")  # Inform the user they can type 'quit' to exit the chat

# Start a loop to continuously receive input from the user
while True:
    user_input = input("You: ")  # Prompt the user to enter a message
    if user_input.lower() == 'quit':  # If the user types 'quit', break the loop and end the conversation
        break
        
    # Add the user's message to the 'messages' list as a HumanMessage
    messages.append(HumanMessage(content=user_input))
    
    # Save the user's message to the 'messages' table in Supabase
    supabase.table('messages').insert({
        'conversation_id': conversation_id,  # Link the message to the current conversation by its ID
        'role': 'user',  # Indicate that the message is from the user
        'content': user_input,  # Store the actual content of the user's message
        'created_at': datetime.now().isoformat()  # Set the current timestamp for when the message was created
    }).execute()

    # Get the AI's response by passing the conversation history to the model
    response = model.invoke(messages)
    print("AI:", response.content)  # Print the AI's response

    # Add the AI's response to the 'messages' list as an AIMessage
    messages.append(AIMessage(content=response.content))
    
    # Save the AI's message to the 'messages' table in Supabase
    supabase.table('messages').insert({
        'conversation_id': conversation_id,  # Link the message to the current conversation
        'role': 'assistant',  # Indicate that the message is from the assistant (AI)
        'content': response.content,  # Store the content of the AI's response
        'created_at': datetime.now().isoformat()  # Set the current timestamp for when the message was created
    }).execute()
