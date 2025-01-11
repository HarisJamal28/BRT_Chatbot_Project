document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    const newChatBtn = document.querySelector('.new-chat-btn');
    const clearConversationsBtn = document.querySelector('.clear-conversations');
    const conversationsContainer = document.querySelector('.conversations');
    const voiceBtn = document.getElementById('voice-btn');

    let conversations = JSON.parse(localStorage.getItem('conversations')) || [];
    let currentConversationId = null;
    const userId = 'harisjamal';  // Replace with dynamic user ID if available

    // Initialize Speech Recognition (for voice input)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = true;
        recognition.maxAlternatives = 1;
    } else {
        console.log("Speech Recognition API is not supported in this browser.");
    }

    // Function to create a new conversation
    function createNewConversation() {
        const conversation = {
            id: Date.now(),
            title: 'New Conversation',
            messages: []
        };
        conversations.unshift(conversation);
        currentConversationId = conversation.id;
        saveConversations();
        updateConversationsList();
        clearMessages();
    }

    // Function to save conversations to localStorage
    function saveConversations() {
        localStorage.setItem('conversations', JSON.stringify(conversations));
    }

    // Function to update the conversations list in the sidebar
    function updateConversationsList() {
        conversationsContainer.innerHTML = '';
        conversations.forEach(conv => {
            const div = document.createElement('div');
            div.className = 'conversation-item';
            div.innerHTML = `
                <i class="fas fa-comments"></i>
                <span>${conv.title}</span>
            `;
            div.addEventListener('click', () => loadConversation(conv.id));
            conversationsContainer.appendChild(div);
        });
    }

    // Function to load a conversation
    function loadConversation(id) {
        currentConversationId = id;
        const conversation = conversations.find(c => c.id === id);
        clearMessages();
        if (conversation) {
            conversation.messages.forEach(msg => {
                addMessage(msg.text, msg.isUser, false);  // false to prevent re-saving to backend
            });
        }
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    }

    // Function to clear messages
    function clearMessages() {
        chatMessages.innerHTML = ` 
            <div class="message bot">
                <div class="message-content">
                    <i class="fas fa-bus message-icon"></i>
                    <div class="text">
                        Hello! I am Zu BRT Companion, Please tell me what BRT Stop you are nearest to so i can help you take the right bus!
                    </div>
                </div>
            </div>
        `;
    }

    // Function to add a message to the chat
    function addMessage(message, isUser = false, saveToBackend = true) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <i class="fas ${isUser ? '' : 'fa-bus'} message-icon"></i>
                <div class="text">${message}</div>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Save message to current conversation
        if (currentConversationId) {
            const conversation = conversations.find(c => c.id === currentConversationId);
            if (conversation) {
                conversation.messages.push({ text: message, isUser });
                if (conversation.messages.length === 2) {
                    // Update conversation title based on first user message
                    conversation.title = message.substring(0, 30) + (message.length > 30 ? '...' : '');
                    updateConversationsList();
                }
                saveConversations();
            }
        }

        // Send chat data to backend for saving in MongoDB if saveToBackend is true
        if (saveToBackend) {
            saveChatToBackend(userId, message, isUser);
        }
    }

    // Function to save chat data to backend
    async function saveChatToBackend(userId, message, isUser) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    message: message,
                    role: isUser ? 'user' : 'assistant'
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    // Function to clear chat history in MongoDB
    async function clearChatHistoryInBackend() {
        try {
            const response = await fetch('/chat/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }

    // Function to show loading animation
    function showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot';
        loadingDiv.innerHTML = `
            <div class="message-content">
                <i class="fas fa-bus message-icon"></i>
                <div class="loading">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return loadingDiv;
    }

    // Function to send message to backend
    async function sendMessage(message) {
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            return data.response;
        } catch (error) {
            console.error('Error:', error);
            return 'Sorry, I encountered an error. Please try again.';
        }
    }

    // Handle send button click
    async function handleSend() {
        const message = userInput.value.trim();
        if (!message) return;

        // Create new conversation if none exists
        if (!currentConversationId) {
            createNewConversation();
        }

        // Clear input
        userInput.value = '';

        // Add user message to chat
        addMessage(message, true);

        // Show loading animation
        const loadingDiv = showLoading();

        // Send message to backend and get response
        const response = await sendMessage(message);

        // Remove loading animation
        loadingDiv.remove();

        // Add bot response to chat
        addMessage(response);
    }

    function handleVoiceInput() {
        if (recognition) {
            recognition.start(); // Start voice recognition
            recognition.onstart = () => {
                console.log('Voice recognition started');
                // Add the 'recording' class to show visual feedback
                voiceBtn.classList.add('recording');
                // alert("Started Voice Recording!")
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                userInput.value = transcript; // Set the transcribed text to the input field
                console.log('Voice Input:', transcript);
            };

            recognition.onerror = (event) => {
                console.log('Speech recognition error', event);
                // You could also stop the recording in case of error to give feedback
                voiceBtn.classList.remove('recording');
            };

            recognition.onend = () => {
                console.log('Voice recognition ended');
                // Remove the 'recording' class once recording stops
                voiceBtn.classList.remove('recording');
            };
        }
    }

    // Event listeners
    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    });

    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });

    newChatBtn.addEventListener('click', createNewConversation);

    clearConversationsBtn.addEventListener('click', async () => {
        conversations = [];
        saveConversations();
        updateConversationsList();
        currentConversationId = null;
        clearMessages();

        // Clear chat history in MongoDB
        await clearChatHistoryInBackend();
    });

    // Add voice button listener
    voiceBtn.addEventListener('click', handleVoiceInput);

    // Initialize
    updateConversationsList();
    if (conversations.length > 0) {
        loadConversation(conversations[0].id);
    }
});


