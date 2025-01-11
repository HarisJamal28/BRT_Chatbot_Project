import os
import shutil
import json
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

load_dotenv()

def load_chunks(docs):
    embeddings = OpenAIEmbeddings(
        model='text-embedding-ada-002'
    )
    if os.path.exists("./chromaDB"):
        shutil.rmtree("./chromaDB")
        print("Existing ChromaDB directory removed.")

    vectorstore = Chroma(
        embedding_function=embeddings,
        collection_name="brtcollection",
        persist_directory="./chromaDB"
    )

    vectorstore.add_documents(docs)
    print(f"Documents added to ChromaDB: {len(docs)} documents")

def load_brt_data():
    with open('./brt_buses_data.json', 'r') as f:
        data = json.load(f)

    docs = [Document(page_content=str(fund), metadata={}) for fund in data]

    load_chunks(docs)

def retriever(question: str):
    embeddings = OpenAIEmbeddings(
        model='text-embedding-ada-002'
    )
    vectorstore = Chroma(
        embedding_function=embeddings,
        collection_name="brtcollection",
        persist_directory="./chromaDB"
    )

    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(question)
    return docs

if __name__ == "__main__":
    load_brt_data()
