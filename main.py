import os
from dotenv import load_dotenv
import openai
import db

# load .env file
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class GPT4ChatBot:
    def __init__(self, engine="gpt-3.5-turbo"):
        self.engine = engine
        self.messages = [
            {
                "role": "system",
                "content": "You are a helpful sales agent for a travel agency.",
            },
            {
                "role": "assistant",
                "content": "Hello and welcome to our travel agency! How can I assist you today?",
            },
        ]

    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})
        db.insert_message(conn, "User", message)

    def get_response(self):
        response = openai.ChatCompletion.create(
            model=self.engine, messages=self.messages
        )
        bot_response = response["choices"][0]["message"]["content"]
        self.messages.append({"role": "assistant", "content": bot_response})
        db.insert_message(conn, "Bot", bot_response)
        return bot_response


def main():
    global conn
    conn = db.create_connection()
    if conn is not None:
        db.create_table(conn)
        chatbot = GPT4ChatBot()
        print("Bot: " + chatbot.get_response())
        while True:
            message = input("User: ")
            if message.lower() == "quit":
                chatbot.add_user_message(
                    "Now, reiterate the most imporatant information in list form."
                )
                print("Bot: " + chatbot.get_response())
            chatbot.add_user_message(message)
            print("Bot: " + chatbot.get_response())
        conn.close()
    else:
        print("Cannot create database connection.")


if __name__ == "__main__":
    main()
