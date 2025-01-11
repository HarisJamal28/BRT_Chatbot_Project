# 🚍 BRT Chatbot
Welcome to the BRT_Buses Chatbot, a project developed as part of the Computational Intelligence course. This project aims to transform the way people navigate Peshawar's Zu BRT public transport system, providing users with a smart, interactive experience for planning their commute.

## 📊 Project Overview
This project is designed to make it easier for users to navigate the Zu BRT system in Peshawar. The BRT_Buses Chatbot acts as a virtual guide, assisting users in making the most of the city's public transportation network. The chatbot is capable of:

- *Guiding users on the different bus routes available.*

- *Recommending the ideal bus routes based on user queries.*

- *Suggesting connected routes to ensure efficient travel.*

- *With its user-friendly interface and seamless functionality, this chatbot is a valuable tool for anyone using Zu BRT.*

## 🤝 Team Contributions
- **Backend Development:** Haris Jamal

- **Frontend Development:** Rahim Shah

## ✨ Features
This project integrates OpenAI's powerful embeddings to enhance the chatbot's ability to understand and respond to complex user queries, using Chroma and LangChain Vectorstore for efficient data retrieval.

The user interface of this chatbot is designed with simplicity and clarity in mind, ensuring a smooth and engaging user experience. The clean layout and easy-to-navigate features make it a pleasure to interact with.

This chatbot supports voice input, allowing users to speak their queries rather than typing them, making the experience even more user-friendly and interactive.

## Technologies Used
🚀 Python
				💡 LangChain	🔐 ChromaDB
🌍 OpenAI

🖥️ HTML
				🎨 CSS	⚡ JavaScript
🗃️ JSON

🗄️ MongoDB
				🗣️ SpeechRecognition

## 📂Project Structure

```
venv Data
├── chromadb/               # Persistent vectorstore data
├── server.py               # FastAPI and Static Files Server
├── brt_llm.py.py           # Chatbot Implementation
├── brt_mongo.py           	# Manages Chat History Storage
├── chatbotbrt.py           # Manages Interactions With Chatbot
├── chromadb_BRT.py         # Loading and Indexing into Chroma Vector DB
├── openai_services.py      # Function To Interact with OpenAI
├── requirements.txt       	# Dependencies
├── .env                   	# Environment variables
├── brt_buses_data.json     # JSON file for Chatbot data
└── README.md              # Project documentation
```

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/HarisJamal28/BRT_Chatbot_Project.git
cd BRT_Chatbot_Project
```

### 2. Install Dependencies
Ensure you have Python installed, then run:
```bash
pip install -r requirements.txt
```

### 3. Prepare the Environment
Create a `.env` file to store your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key
```

### 4. Run the Chatbot
To start the chatbot, execute:
```bash
python server.py
```
The User Interface will be accessible at `http://localhost:8000`.

## 📊 Data Sources
The chatbot is powered by a JSON document.

## 🚀 Deployment
This chatbot is expected to be deployed using Vercel, Railway or AWS

## 🤝 Acknowledgments
This Project was a result of our Computational Intelligence Semester Project.

## 📝 License
This project is open-source and available under the MIT License.

## 💬 Feedback
Feel free to open issues or create pull requests for any suggestions or improvements!
---

### ⭐ Give this repository a star if you found it helpful!
---

**Authors:**
- Haris Jamal
- Rahim Shah
