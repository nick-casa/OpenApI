from flask import render_template, request, jsonify
from app import app
from .chatbot import run_message
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime

load_dotenv()
uri = os.getenv("MONGO_URI")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Select your database
db = client['magiccarpet_ib']

def add_user(user_id):
    db.users.insert_one({"user_id": user_id})

def log_message(user_id, messages):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.messages.insert_one({"user_id": user_id, "messages": messages, "timestamp": timestamp})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    user_id = str(uuid.uuid4())
    add_user(user_id)
    messages = [
        {
            "role": "system",
            "content": """ You are a travel agent that is helping a user plan a trip; Your job is only to plan a trip.
                        Please ensure all completions are in line with this objective.

                        Start the conversation by greeting the user.
                        Early on in the conversation with the user, collect their name and email and call function to log user AS SOON AS INFO IS RETRIEVED.
                        Before concluding the conversation, work with the user to make a general itinerary; DO NOT GET INTO SPECIFICS.
                        Then, when the user is satisfied with the itinerary, email it to them.
                        At the same time, email the sales rep with the summary of your conversation with the user.

                        Throughout the conversation, retrieve the following pieces of information
                        NAME, EMAIL, DEPARTING LOCATION, DESTINATION, DATES, and BUDGET.

                        Here are some more questions that you can (but do not have to) incorporate:
                        DESTINATION: Where would you like to go on vacation?
                        DURATION: How long do you plan to stay there?
                        ACCOMODATION: What type of accommodation do you prefer? (Hotel, Resort, etc.)
                        INTERESTS: What are your main interests or activities you'd like to engage in during the vacation?
                        SIGHTSEEING: Are there any specific landmarks, attractions, or places you'd like to visit?
                        TRAVEL COMPANIONS: Will you be traveling alone or with others? If with others, how many people and their preferences?
                        PREFERRED ACTIVITIES: What activities would you like to engage in during your vacation?
                        CULTURAL EXPERIENCES: Are you interested in immersing yourself in the local culture, traditions, or trying local cuisines?

                        DO NOT PROVIDE CODE, JSON, OR SIMILAR SYNTAX UNDER ANY CIRCUMSTANCE
                        """
        }
    ]
    log_message(user_id, messages)
    return jsonify({"user_id": user_id, "messages": run_message(messages)})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if data and 'messages' in data and 'user_id' in data:
        messages = data['messages']
        user_id = data['user_id']
        log_message(user_id, messages)
        return jsonify(run_message(messages))
    else:
        return 'No message or user id received', 400

