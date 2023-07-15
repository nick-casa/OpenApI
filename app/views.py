from flask import render_template, request, jsonify, make_response,send_from_directory, redirect
from app import app
from .chatbot import run_message
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime
import requests

load_dotenv()
uri = os.getenv("MONGO_URI")
clientID = os.getenv("GHL_APP_CLIENT_ID")
clientSecret = os.getenv("GHL_APP_CLIENT_SECRET")
baseURL = os.getenv("BASE_URL")


# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['magiccarpet_ib']

def add_user(user_id):
    db.users.insert_one({"user_id": user_id})

def log_message(user_id, messages):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.messages.insert_one({"user_id": user_id, "messages": messages, "timestamp": timestamp})

def get_last_conversation(user_id):
    # Query the database for the user's messages, sorting by timestamp in descending order
    # Here it's assumed your message documents have a 'user_id' field and a 'timestamp' field
    user_messages = db.messages.find({"user_id": user_id}).sort("timestamp", DESCENDING)

    # Return the most recent message, if it exists
    if user_messages.count() > 0:
        return user_messages[0]
    else:
        return None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    user_id = request.cookies.get('user_id')
    data = request.json
    new_convo = data.get('new_convo')

    if user_id is None:
        user_id = str(uuid.uuid4())
        add_user(user_id)

    if new_convo:
        messages = [
            {
            "role": "system",
            "content": """ You are a travel agent that is helping a user plan a trip; Your job is only to plan a trip.
                        Please ensure the conversation stays in line with this objective.
                        Before concluding the conversation, work with the user to make a generalized itinerary; DO NOT GET INTO SPECIFICS.
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
                        After the information is collected and the questions are discussed, summarize the conversation and save the preferences.
                        DO NOT PROVIDE CODE, JSON, OR SIMILAR SYNTAX UNDER ANY CIRCUMSTANCE

                        Throughout the conversation, AS SOON AS INFORMATION IS GIVEN BY USER, call the three functions:
                        retrieved_user_info, retrieved_user_preferences, and generated_itinerary.

                        Start the conversation by greeting the user then asking for their name and email.

                        """
            }
        ]
    else:
        messages = get_last_conversation(user_id)['messages']

    log_message(user_id, messages)

    response = make_response(jsonify({"user_id": user_id, "messages": run_message(messages, user_id)}))
    response.set_cookie('user_id', user_id, max_age=60*60*24*30) # set cookie to expire after 30 days
    return response


@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if data and 'messages' in data and 'user_id' in data:
        messages = data['messages']
        user_id = data['user_id']
        log_message(user_id, messages)
        return jsonify(run_message(messages, user_id))
    else:
        return 'No message or user id received', 400

@app.route('/stylesheet.css')
def serve_stylesheet():
    return send_from_directory(app.static_folder, 'css/chatbot.css')


@app.route('/initiateAuth')
def initiate_auth():
    options = {
        'requestType': 'code',
        'redirectUri': 'https://ib.mctravels.com/gohighlevel/oauth',
        'clientId': clientID,
        'scopes': [
            'conversations.write',
            'contacts.write',
            'conversations/message.write'
        ]
    }
    return redirect(f"{baseURL}/oauth/chooselocation?response_type={options['requestType']}&redirect_uri={options['redirectUri']}&client_id={options['clientId']}&scope={' '.join(options['scopes'])}")

@app.route('/gohighlevel/oauth')
def gohighlevel_oauth():
    code = request.args.get('code')
    data = {
        'client_id': clientID,
        'client_secret': clientSecret,
        'grant_type': 'authorization_code',
        'code': code,
        'user_type': 'Location',
        'redirect_uri': 'http://localhost:3000/oauth/callback'
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.post('https://services.leadconnectorhq.com/oauth/token', data=data, headers=headers)

    if response.status_code != 200:
        # If some error occurs
        return jsonify({'error': 'An error occurred.'})

    return jsonify({'data': response.json()})