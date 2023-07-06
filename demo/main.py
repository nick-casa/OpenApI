import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def send_email_to_rep(email_address, travel_preferences,name,budget):
    print("------- sent email to rep ------")
    print(name)
    print(email_address)
    print(travel_preferences)
    print(budget)

    """Send an email to a sales representative with the user's travel preferences"""
    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the representative successfully!"})

def send_email_to_user(email_address, travel_itinerary):
    print("------- sent email to user ------")
    print(travel_itinerary)
    """Send an email to the user with a rough travel itinerary"""
    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the user successfully!"})

def run_conversation(messages):
    model = "gpt-3.5-turbo-0613"
    functions = [
        {
            "name": "send_email_to_rep",
            "description": "Send an email to a sales representative with the lead's information and travel preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_address": {
                        "type": "string",
                        "description": "Email address of the sales representative",
                    },
                    "name": {
                        "type": "string",
                        "description": "User's name",
                    },
                    "budget": {
                        "type": "string",
                        "description": "User's budget",
                    },
                    "travel_preferences": {
                        "type": "string",
                        "description": "User's travel preferences",
                    },
                },
                "required": ["email_address", "travel_preferences", "budget", "name"],
            },
        },
        {
            "name": "send_email_to_user",
            "description": "Send an email to the user with a detailed example travel itinerary",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_address": {
                        "type": "string",
                        "description": "Email address of the user",
                    },
                    "travel_itinerary": {
                        "type": "string",
                        "description": "Example itinerary of the entire trip by day",
                    },
                },
                "required": ["email_address", "travel_itinerary"],
            },
        },
    ]

    while True:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call="auto",
        )
        response_message = response["choices"][0]["message"]

        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            function_args = json.loads(response_message["function_call"]["arguments"])
            available_functions = {
                "send_email_to_rep": send_email_to_rep,
                "send_email_to_user": send_email_to_user,
            }
            function_to_call = available_functions[function_name]
            function_response = function_to_call(**function_args)
            messages.append(response_message)
            messages.append(
                {
                    "role": "function",
                    "name": function_name,
                    "content": function_response,
                }
            )
        else:
            print("GPT:", response_message["content"])
            messages.append({"role": "assistant", "content": response_message["content"]})
            user_input = input("You: ")
            messages.append({"role": "user", "content": user_input})


messages = [
    {
        "role": "system",
        "content": """You are a helpful travel agent that is helping plan a trip. Throughout the conversation, retrieve the following pieces of information
                    (along with any other pieces of information you may need to plan a trip): NAME, EMAIL, DEPARTING LOCATION, DESTINATION, DATES, and BUDGET.
                    Before conclusing the conversation, email the user an itinerary."""
    }
]
run_conversation(messages)
