import os
from flask import Flask, request, jsonify, g
from dotenv import load_dotenv
import openai
from db import get_db, create_conversation_table, create_users_table, insert_message, insert_user, get_conversation_history

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
app.config.from_mapping(
    DATABASE=os.path.join(app.instance_path, "chatbot_database.db")
)

def get_chatbot():
    if "chatbot" not in g:
        g.chatbot = GPT4ChatBot()
    return g.chatbot

class GPT4ChatBot:
    def __init__(self, engine="gpt-3.5-turbo"):
        self.engine = engine

    def get_chat_history(self, user_id):
        db = get_db()
        chat_history = get_conversation_history(db, user_id)
        if not chat_history:
            insert_user(db, user_id)
            chat_history = []
        return chat_history

    def add_user_message(self, user_id, message):
        db = get_db()
        insert_message(db, user_id, "user", message)

    def get_response(self, user_id):
        db = get_db()
        chat_history = self.get_chat_history(user_id)
        messages = [{"role": msg[0], "content": msg[1]} for msg in chat_history]
        if not messages:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful sales agent for a travel agency.",
                }
            ]
        else:
            messages.append({"role": "user", "content": messages[-1]["content"]})
        response = openai.ChatCompletion.create(
            model=self.engine, messages=messages
        )
        bot_response = response.choices[0].message.content
        insert_message(db, user_id, "assistant", bot_response)
        return bot_response

@app.route('/message', methods=['POST'])
def receive_message():
    user_id = request.form['user_id']
    user_message = request.form['message']
    chatbot = get_chatbot()
    chatbot.add_user_message(user_id, user_message)
    bot_response = chatbot.get_response(user_id)
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    with app.app_context():
        create_conversation_table(get_db())
        create_users_table(get_db())
    app.run(port=5001)
