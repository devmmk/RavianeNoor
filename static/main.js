document.getElementById('send-btn').addEventListener('click', sendMessage);
document.getElementById('message-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

async function sendMessage() {
    const messageInput = document.getElementById('message-input');
    const messageText = messageInput.value.trim();
    
    if (messageText === "") return;

    // Create a new message element
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'user');
    messageElement.textContent = messageText;

    // Append message to the chat box
    const chatBox = document.getElementById('chat-box');
    chatBox.appendChild(messageElement);

    // Scroll to the bottom of the chat box
    chatBox.scrollTop = chatBox.scrollHeight;

    // Clear the input field
    messageInput.value = "";

    // Get bot response
    const botMessageElement = document.createElement('div');
    botMessageElement.classList.add('message', 'bot');
    
    try {
        const response = await getBotResponse(messageText);
        botMessageElement.textContent = response;
    } catch (error) {
        botMessageElement.textContent = "متاسفم، سقف استفاده روزانه شما پر شده است.";
    }

    chatBox.appendChild(botMessageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}



async function getBotResponse(userMessage) {
    if (!userMessage) return "لطفا پیام خود را بنویسید";
    
    const formData = new FormData();
    formData.append('message', userMessage);
    console.log(userMessage);
    const response = await fetch('/ai', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('خطا در دریافت پاسخ از سمت سرور');
    }
    
    return await response.text();
}
