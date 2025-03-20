from source.functions import load_pdf, text_split, download_hugging_face_embeddings
from langchain_community.vectorstores import FAISS
import os

extracted_data = load_pdf("data/")
text_chunks = text_split(extracted_data)
print("length of my chunk:", len(text_chunks))
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

query = "what might be the reasons for fever?"
docs = db.similarity_search(query, k=2)

print("Relevant Documents Found:")
for i, doc in enumerate(docs):
    print(f"\nResult {i+1}:")
    print(doc.page_content)
    print("Source:", doc.metadata["source"])
