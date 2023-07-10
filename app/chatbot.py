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
    return json.dumps({"status": "user information saved!"})

def retrieved_user_preferences(name, email, departing_location, destination, dates, budget, summary, **args):
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
    return json.dumps({"status": "user preferences saved and sent to travel agent!"})

def generated_itinerary(itinerary, **args):
    print("------- User itinerary generated ------")
    db.users.update_one(
        {"user_id": args['user_id']},
        {"$set": {"itinerary":itinerary}},
        upsert=True
    )
    return json.dumps({"status": "itinerary sent to user!"})

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
                "required": ["name", "email", "departing_location", "destination", "dates", "budget", "summary"],
            },
        },
        {
            "name": "generated_itinerary",
            "description": "Trigger this function once the travel itinerary has been generated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "itinerary": {
                        "type": "string",
                        "description": """Preliminary Itinerary to be emailed to the traveler, as agreed in the chat. Match the style and thoroughness.

                                            Thank you for starting your journey with Magic Carpet Travel.  I look forward to fine tuning this itinary with you.  Like planning specific restaurants etc.
                                            Kellie Pustizzi
                                            Day 1-3: Barcelona
                                            Fly from Philadelphia to Barcelona.
                                            Check into a luxurious 5-star hotel in a safe area.
                                            Explore the Gothic Quarter, visit Barcelona Cathedral, and stroll along Las Ramblas.
                                            Discover the architectural marvel of Sagrada Familia.
                                            Enjoy the beach at Barceloneta and try local seafood.
                                            Experience vibrant local traditions and dine at top local restaurants.
                                            Day 4-6: Costa Brava (Beach Town)
                                            Rent a car and drive to the beautiful Costa Brava region.
                                            Stay in a 5-star beachfront hotel for 2 nights.
                                            Relax on the stunning beaches of towns like Tossa de Mar and Cadaqués.
                                            Visit the Dali Theatre-Museum in Figueres and explore the artist's hometown.
                                            Enjoy coastal walks, water sports, and local cuisine.

                                            Day 7-9: Seville (Historic City)
                                            Fly from Barcelona to Seville.
                                            Check into a luxurious 5-star hotel in a central location.
                                            Explore the historic center, including the Seville Cathedral and Giralda Tower.
                                            Wander through the narrow streets of Santa Cruz neighborhood.
                                            Visit the Royal Alcazar, a magnificent Moorish palace.
                                            Immerse yourself in local traditions, watch Flamenco performances, and savor Andalusian cuisine.
                                            Day 10: Valencia (Beach Town and Historic Area)
                                            Take a high-speed train from Seville to Valencia.
                                            Stay in a 5-star hotel near the beach.
                                            Visit the futuristic City of Arts and Sciences.
                                            Explore the historic Valencia Cathedral and climb the Micalet Tower.
                                            Enjoy the beach, relax, and try local Valencian cuisine.
                                            Day 11: Departure

                                            Fly from Valencia back to Philadelphia, concluding your trip to Spain.

                                            This itinerary allows you to experience the best of Spain, combining beach towns and historic areas. Starting in Barcelona, you'll explore the city's iconic landmarks and enjoy the beach. Then, you'll head to Costa Brava for a relaxing beach stay. In Seville, you'll immerse yourself in the city's rich history and vibrant traditions. Finally, you'll visit Valencia for a mix of beachside relaxation and cultural exploration. Throughout your journey, you'll stay in luxurious 5-star hotels, dine at top local restaurants, and have the opportunity to experience local traditions.""",
                    }
                },
                "required": ["itinerary"],
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
    if  response_message["content"]:
        messages.append({"role": "assistant", "content": response_message["content"]})
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
            "generated_itinerary": generated_itinerary,
        }

        function_to_call = available_functions[function_name]
        function_response = function_to_call(user_id=user_id, **function_args)

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
        messages.append({"role": "assistant", "content": response_message["content"]})


    return messages

