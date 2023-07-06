import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def respond_to(message):
    # Logic for generating a response goes here
    return "I'm a chatbot!"

def send_email_to_rep(name, email, departing_location, destination, dates, budget):
    print("------- sent email to rep ------")
    print(json.dumps({"name": name,
                        "email": email,
                        "departing": departing_location,
                        "destination":destination,
                        "dates":dates,
                        "budget":budget}))

    """Send an email to a sales representative with the user's travel preferences"""
    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the representative successfully!"})

def send_email_to_user(email_address, name, travel_itinerary):
    print("------- sent email to user ------")
    print(json.dumps({"name": name,
                        "email": email_address,
                        "itinerary": travel_itinerary}))

    # Implement your email sending logic here
    return json.dumps({"status": "Email sent to the user successfully!"})

def run_message(messages):
    model = "gpt-3.5-turbo-0613"
    functions = [
        {
            "name": "send_email_to_rep",
            "description": "Send an email to a sales representative with the lead's information and travel preferences",
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
                },
                "required": ["email_address", "departing_location", "budget", "name", "dates", "destination"],
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
                    "name": {
                        "type": "string",
                        "description": "Full name of the user",
                    },
                    "travel_itinerary": {
                        "type": "string",
                        "description": "Example itinerary of the entire trip by day",
                    },
                },
                "required": ["email_address", "travel_itinerary", "name"],
            },
        },
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
        messages.append({"role": "assistant", "content": response_message["content"]})

    return messages

