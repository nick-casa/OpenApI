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
            data.forEach(message => { addMessageToChat(message.role, message.content) }) ;
        }
        console.log(messageLog);
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
                if (lastMessage.role == "assistant") {
                    setTimeout(() => {
                    liBotTyping.innerHTML = `Travel Agent: ${lastMessage.content.split('\n').join('<br>')}`;
                }, 2000);  // replace the typing indicator with the message after a delay
                    messageLog.push(lastMessage);
                    console.log(messageLog)
                }
            }
        });

        // clear input field
        document.querySelector('#message-input').value = '';

        // stop form from submitting
        return false;
    };
});

function addMessageToChat(sender, message) {
    messageLog.push({ role: sender, content: message });
    if (sender == "assistant" || sender == "user") {
        const li = document.createElement('li');

        let senderDict = { "assistant": "bot", "user": "user" };
        let innerDict = { "assistant": "Travel Agent", "user": "You" };

        li.className = `message-${senderDict[sender]}`;
        li.innerHTML = `${innerDict[sender]}: ${message.split('\n').join('<br>')}`;
        console.log(message);
        document.querySelector('#chatbox').append(li);
    }
}