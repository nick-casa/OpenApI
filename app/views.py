from flask import render_template, request, jsonify, make_response,send_from_directory, redirect
from app import app
from .chatbot import run_message
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timedelta
import requests
from bson.objectid import ObjectId


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
        print(f"Error: Received status code {response.status_code} from token request")
        print(f"Response text: {response.text}")
        return jsonify({'error': 'An error occurred.'})

    token_data = response.json()

    # Get the current date and time
    current_date = datetime.now()

    # Compute the expiration date
    expires_in_seconds = token_data.get('expires_in', 0)
    expiration_date = current_date + timedelta(seconds=expires_in_seconds)

    # Add these dates to the token data
    token_data['current_date'] = current_date
    token_data['expiration_date'] = expiration_date

    db.auth_tokens.insert_one(token_data)

    # Convert ObjectId to string before returning it in the response
    if "_id" in token_data:
        token_data["_id"] = str(token_data["_id"])

    print(f"Successfully inserted token data into auth_tokens collection: {token_data}")

    return jsonify({'data': token_data})


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

@app.route('/refreshToken')
def refresh_token(token_id):
    token_id=request.args.get("token_id")
    # Get the token data from the database
    token_data = db.auth_tokens.find_one({"_id": ObjectId(token_id)})
    if token_data is None:
        return jsonify({'error': 'Token not found.'}), 404

    refresh_token = token_data.get('refresh_token')
    if refresh_token is None:
        return jsonify({'error': 'Refresh token not found in the token data.'}), 404

    # Prepare the data for the token refresh request
    data = {
        'client_id': clientID,
        'client_secret': clientSecret,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'user_type': 'Location',
        'redirect_uri': 'http://localhost:3000/oauth/callback'
    }

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the token refresh request
    response = requests.post('https://services.leadconnectorhq.com/oauth/token', data=data, headers=headers)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from token refresh request")
        print(f"Response text: {response.text}")
        return jsonify({'error': 'An error occurred.'}), response.status_code

    new_token_data = response.json()

    # Compute the new expiration date
    expires_in_seconds = new_token_data.get('expires_in', 0)
    new_expiration_date = datetime.now() + timedelta(seconds=expires_in_seconds)

    # Update the token data
    new_token_data['current_date'] = datetime.now()
    new_token_data['expiration_date'] = new_expiration_date

    # Update the token data in the database
    db.auth_tokens.update_one({"_id": ObjectId(token_id)}, {"$set": new_token_data})

    # Convert ObjectId to string before returning it in the response
    if "_id" in new_token_data:
        new_token_data["_id"] = str(new_token_data["_id"])

    print(f"Successfully refreshed and updated token data in auth_tokens collection: {new_token_data}")

    return jsonify(new_token_data)

@app.route('/get_token/<token_id>', methods=['GET'])
def get_token(token_id):
    token_doc = db.auth_tokens.find_one({"_id": ObjectId(token_id)})

    # Check if the token exists
    if token_doc:
        # Convert ObjectId to string before returning it in the response
        token_doc["_id"] = str(token_doc["_id"])
        return jsonify({"data": token_doc})
    else:
        return jsonify({"error": "No token found for this user"}), 404


@app.route('/get_valid_token', methods=['GET'])
def get_valid_token_route():

    # Get the most recent token, regardless of whether it has expired
    token_doc = db.auth_tokens.find_one({}, sort=[("created_at", DESCENDING)])

    # Check if a token was found
    if token_doc:
        # Check if the token has expired
        if token_doc["expiration_date"] < datetime.utcnow():
            # If the token has expired, refresh it
            refreshed_token = refresh_token(str(token_doc["_id"]))

            if not refreshed_token:
                return jsonify({"error": "Failed to refresh token"}), 500

            return refreshed_token

        # If the token has not expired, return it
        return get_token(str(token_doc["_id"]))
    else:
        return jsonify({"error": "No token found"}), 404
