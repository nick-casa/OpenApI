from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import openai
import json
import os

# Retrieve sensitive data
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['magiccarpet_ib']

## GPT Functions
def retrieved_user_info(email, name, **args):
    print("------- User Information Retrieved ------")
    db.users.update_one(
        {"user_id": args['user_id']},
        {"$set": {"name": name, "email": email}},
        upsert=True
    )
    return json.dumps({"status": "Function called successfully!"})

def retrieved_user_preferences(name, email, departing_location, destination, dates, budget,summary, **args):
    print("------- User Preferences Retrieved ------")
    db.users.update_one(
        {"user_id": args['user_id']},
        {"$set": {"departing": departing_location,
                    "destination": destination,
                    "dates": dates,
                    "budget": budget,
                    "summary": summary}},
        upsert=True
    )
    return json.dumps({"status": "Function called successfully!"})

## Conversation Function
def run_message(messages, user_id):
    model = "gpt-3.5-turbo-0613"
    functions = [
        {
            "name": "retrieved_user_info",
            "description": "Trigger this function once user's name and email have been collected.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "User's email address",
                    },
                    "name": {
                        "type": "string",
                        "description": "User's full name",
                    },
                },
                "required": ["email", "name"],
            },
        },
        {
            "name": "retrieved_user_preferences",
            "description": "Trigger this function once user's travel preferences have been collected.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "User's email address",
                    },
                    "name": {
                        "type": "string",
                        "description": "User's full name",
                    },
                    "departing_location": {
                        "type": "string",
                        "description": "User's travel departing location",
                    },
                    "destination": {
                        "type": "string",
                        "description": "User's travel destination",
                    },
                    "dates": {
                        "type": "string",
                        "description": "User's travel start/end dates",
                    },
                    "budget": {
                        "type": "string",
                        "description": "User's travel budget",
                    },
                    "summary": {
                        "type": "string",
                        "description": "a bulleted summary of the important points of the conversation",
                    },
                },
                "required": ["email", "departing_location", "budget", "name", "dates", "destination","additional_information"],
            },
        }
    ]

    response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call="auto",
    )
    response_message = response["choices"][0]["message"]

    if response_message.get("function_call"):
        function_name = response_message["function_call"]["name"]

        try:
            function_args = json.loads(response_message["function_call"]["arguments"])
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            print(f"Original string: {response_message['function_call']['arguments']}")

        available_functions = {
            "retrieved_user_preferences": retrieved_user_preferences,
            "retrieved_user_info": retrieved_user_info,
        }

        function_to_call = available_functions[function_name]
        function_response = function_to_call(user_id=user_id,**function_args)

        messages.append(response_message)
        messages.append(
            {
                "role": "function",
                "name": function_name,
                "content": function_response
            }
        )

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        response_message = response["choices"][0]["message"]
        print(response)

    messages.append({"role": "assistant", "content": response_message["content"]})

    return messages

