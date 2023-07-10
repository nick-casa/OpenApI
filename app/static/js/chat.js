let messageLog = [];

// The getCookie function
function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) {
            console.log("user found")
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function startConversation(newConvo) {
    // Call /start_conversation to have the bot initiate the conversation
    fetch('/start_conversation', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'new_convo': newConvo
        })
    })
    .then(response =>  response.json())
    .then(data => {
        let messages;
        if (data.messages) {
            messages = data.messages;
        }
        if (data.user_id) {
            user_id = data.user_id;
        }
        // add bot's initial message(s) or last conversation to the chat
        if (messages && messages.length > 0) {
            messages.forEach(message => { addMessageToChat(message.role, message.content) }) ;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    let user_id = getCookie('user_id');

    if (user_id) {
        const continueChat = confirm("Would you like to continue your last conversation?");
        if (continueChat) {
            console.log("false")
            // The user wants to continue the last chat, so load it up
            startConversation(false);
        }
        else {
            startConversation(true);
        }
    }
    else {
        startConversation(true);
    }

    document.querySelector('#message-form').onsubmit = () => {
        // create new item for list
        const userMessage = document.querySelector('#message-input').value;
        addMessageToChat('user', userMessage);

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
                'messages': messageLog,
                'user_id': user_id
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            // add bot's response to the chat
            if (data && data.length > 0) {
                console.log(data);
                const lastMessage = data[data.length - 1];
                if (lastMessage.role == "assistant") {
                    let wordCount = lastMessage.content.trim().split(/\s+/).length;
                    setTimeout(() => {
                        liBotTyping.innerHTML = `Travel Agent: ${lastMessage.content.split('\n').join('<br>')}`;
                    }, wordCount * 0.0025);  // replace the typing indicator with the message after a delay
                    messageLog.push(lastMessage);
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