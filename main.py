from flask import Flask, render_template, jsonify, request
from source.functions import load_pdf, text_split, download_hugging_face_embeddings
from langchain_community.vectorstores import FAISS
import os
from langchain.prompts import PromptTemplate
from langchain.llms import CTransformers
from langchain.chains import RetrievalQA
from source.prompt import *


app = Flask(__name__)

embeddings = download_hugging_face_embeddings()



DB_FAISS_PATH = "vectorstore/db_faiss"

# Create Folder if not exists
os.makedirs(DB_FAISS_PATH, exist_ok=True)

try:
    print(f"Number of Chunks: {len(text_chunks)}")

    print("Creating FAISS Vector Store...")

    db = FAISS.from_documents(text_chunks, embeddings)
    
    # Save FAISS DB Locally
    db.save_local(DB_FAISS_PATH)
    print("FAISS Vector Store Created Successfully")

except Exception as e:
    print("Error while creating FAISS Vector Store:", str(e))


# Load FAISS Vector Store 
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

from langchain_huggingface import HuggingFaceEndpoint


# Step 1: Setup LLM (Mistral with HuggingFace)
HF_TOKEN=os.environ.get("HF_TOKEN")
HUGGINGFACE_REPO_ID="mistralai/Mistral-7B-Instruct-v0.3"

def load_llm(huggingface_repo_id):
    llm=HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        temperature=0.2,
        model_kwargs={"token":HF_TOKEN,
                      "max_length":"512"}
    )
    return llm


prompt=PromptTemplate(template=prompt_template,input_variables=["context","question"])

# Create QA chain
qa_chain=RetrievalQA.from_chain_type(
    llm=load_llm(HUGGINGFACE_REPO_ID),
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k':3}),
    return_source_documents=True,
    chain_type_kwargs={"prompt":prompt}
)


@app.route("/")
def index():
    return render_template('chat.html')


@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    input = msg
    print(input)
    result = qa_chain.invoke({"query": input})  
    print("Response : ", result["result"])
    return str(result["result"])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port= 5000, debug= True)
