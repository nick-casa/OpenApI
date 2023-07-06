from flask import render_template, request, jsonify
from app import app
from .chatbot import respond_to, run_message

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_conversation', methods=['POST'])
def start_conversation():
    messages = [
        {
            "role": "system",
            "content": """ You are a helpful travel agent that is helping plan a trip. Throughout the conversation, retrieve the following pieces of information
                        (along with any other pieces of information you may need to plan a trip): NAME, EMAIL, DEPARTING LOCATION, DESTINATION, DATES, and BUDGET.
                        Before concluding the conversation, work with the user to make a general itinerary. DO NOT GET INTO SPECIFICS. Then, when the user is satisfied with the itinerary,
                        email it to them and also email the sales rep. Start the conversation by greeting the user. """
        }
    ]
    return jsonify(run_message(messages))

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    if data and 'messages' in data:
        return jsonify(run_message(data['messages']))
    else:
        return 'No message received', 400


