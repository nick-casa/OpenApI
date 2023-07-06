from flask import Flask, request

app = Flask(__name__)

# Chatbot logic
def chatbot_response(message):
    # Add your chatbot logic here
    # You can use any chatbot library or implementation of your choice
    # For simplicity, let's just echo the user's message
    return f"Chatbot: {message}"

# Web server routes
@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_message = request.form['message']
        bot_response = chatbot_response(user_message)
        return f'''
            <h1>Chatbot Demo</h1>
            <p>User: {user_message}</p>
            <p>{bot_response}</p>
            <form method="POST">
                <input type="text" name="message" autofocus/>
                <input type="submit" value="Send" />
            </form>
        '''
    else:
        return '''
            <h1>Chatbot Demo</h1>
            <p>Welcome to the chatbot demo!</p>
            <form method="POST">
                <input type="text" name="message" autofocus/>
                <input type="submit" value="Send" />
            </form>
        '''

if __name__ == '__main__':
    app.run()
