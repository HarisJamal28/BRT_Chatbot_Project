import os
from chromadb_BRT import retriever, load_brt_data
from brt_mongo import save_chat, fetch_chat
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
import time


load_dotenv()

if not os.path.exists("./chromaDB"):
    load_brt_data()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def type_effect(text, delay=0.05):
    """Simulates a typing effect for the chatbot response."""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def bus_bot(user_id):
    llm = ChatOpenAI(model='gpt-4o-mini')
    template = """
    You are a bus route companion. Using the following data:
    {data}

    Provide a concise and structured answer to the user's question:
    {question}

    Ensure the answer is clear, with important details highlighted and formatted in bullet points if necessary.
    """
    prompt = PromptTemplate(template=template, input_variables=["data", "question"])

    while True:
        question = input("Ask a Question (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break

        history = fetch_chat(user_id)
        clean_history = []

        if len(history) > 0:
            for item in history:
                role = 'assistant' if item['role'] == 'assistant' else 'user'
                clean_history.append(
                    {
                        "role": role,
                        "content": item["content"]
                    }
                )

        docs = retriever(question)
        combined_data = format_docs(docs)

        formatted_prompt = prompt.format(data=combined_data, question=question)

        messages = clean_history + [{"role": "user", "content": formatted_prompt}]

        time.sleep(2) 
        response = llm(messages)

        if not response.content:
            response.content = "I wasn't able to find an answer to your query. Could you clarify?"

        type_effect(response.content)  
        user_chat = {"user_id": user_id, "role": "user", "content": question}
        save_chat(user_chat)
        ai_chat = {"user_id": user_id, "role": "assistant", "content": response.content}
        save_chat(ai_chat)

if __name__ == "__main__":
    bus_bot(user_id="harisjamal")
