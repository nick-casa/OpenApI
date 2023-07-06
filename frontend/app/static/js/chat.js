let messageLog = [];

document.addEventListener('DOMContentLoaded', () => {

    // Call /start_conversation to have the bot initiate the conversation
    fetch('/start_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // add bot's initial message(s) to the chat
        if (data && data.length > 0) {
            const lastMessage = data[data.length - 1];
            addMessageToChat(lastMessage.role, lastMessage.content);
            messageLog.push(lastMessage);
            console.log(messageLog);
        }
    });

    document.querySelector('#message-form').onsubmit = () => {
        // create new item for list
        const userMessage = document.querySelector('#message-input').value;
        addMessageToChat('user', userMessage);
        messageLog.push({role: 'user', content: userMessage});

        // create a typing indicator
        const liBotTyping = document.createElement('li');
        liBotTyping.className = 'message-bot';
        liBotTyping.innerHTML = `Travel Agent: <span class="typing-indicator"> ... </span>`;

        const chatBox = document.querySelector('#chatbox');
        chatBox.append(liBotTyping);
        chatBox.scrollTop = chatBox.scrollHeight;  // scroll to bottom

        // send message to server and get response
        fetch('/send_message', {
            method: 'POST',
            body: JSON.stringify({
                'messages': messageLog
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // add bot's response to the chat
            if (data && data.length > 0) {
                const lastMessage = data[data.length - 1];
                setTimeout(() => {
                    liBotTyping.innerHTML = `Travel Agent: ${lastMessage.content}`;
                }, 2000);  // replace the typing indicator with the message after a delay
                messageLog.push(lastMessage);
            }
        });

        // clear input field
        document.querySelector('#message-input').value = '';

        // stop form from submitting
        return false;
    };
});

function addMessageToChat(sender, message) {
    const li = document.createElement('li');

    let senderDict = { "assistant": "bot", "user": "user" };
    let innerDict = { "assistant": "Travel Agent", "user": "You" };

    li.className = `message-${senderDict[sender]}`;
    li.innerHTML = `${innerDict[sender]}: ${message}`;
    document.querySelector('#chatbox').append(li);
}