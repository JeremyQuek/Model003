from flask import Flask, request, jsonify
import os
from langchain_community.document_loaders import SeleniumURLLoader
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain

app = Flask(__name__)
api_key = os.getenv('OpenAI_API_Key')
urls = []

@app.route("/set_url", methods=["POST"])
def set_url():
    new_url = request.json["url"]
    urls.append(new_url)  # Add the new URL to the list
    return jsonify({"message": "URL added successfully"}), 200

@app.route("/query", methods=["POST"])
def query():
    my_query = request.json["question"]

    # Initialize or update the necessary objects
    loader = SeleniumURLLoader(urls=urls)
    webpages = loader.load()
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(webpages, embedding=embeddings)
    my_llm = ChatOpenAI(temperature=1.0, model_name="gpt-3.5-turbo")
    memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=my_llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        memory=memory
    )

    result = conversation_chain({"question": my_query})
    answer = result["answer"]
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True)
