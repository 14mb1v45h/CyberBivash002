document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    let currentConversationId = null;

    chatForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const message = messageInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        messageInput.value = '';

        // Show typing indicator
        typingIndicator.style.display = 'block';

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message: message,
                    conversation_id: currentConversationId
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Store conversation ID
                currentConversationId = data.conversation_id;
                // Add AI response to chat
                addMessage(data.response, 'ai');
            } else {
                // Show error message
                addMessage('Error: ' + (data.error || 'Something went wrong'), 'error');
            }
        } catch (error) {
            addMessage('Error: Could not connect to the server', 'error');
        } finally {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });

    function addMessage(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message-bubble', type + '-message');
        messageDiv.textContent = message;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});