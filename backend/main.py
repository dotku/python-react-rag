import os
import openai
import json
import pprint

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter

# Load environment variables from .env.local and .env
load_dotenv(find_dotenv('.env.local'))
load_dotenv(find_dotenv('.env'))

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Debug prints
print(f"PINECONE_API_KEY: {os.getenv('PINECONE_API_KEY')}")
print(f"PINECONE_ENVIRONMENT: {os.getenv('PINECONE_ENVIRONMENT')}")
print(f"PINECONE_INDEX_NAME: {os.getenv('PINECONE_INDEX_NAME')}")
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"), environment=os.getenv("PINECONE_ENVIRONMENT"))
index_name = os.getenv("PINECONE_INDEX_NAME")

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,
        metric='euclidean'
    )
index = pc.Index(index_name)

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define the model for request and response
class Query(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()
    text = contents.decode('utf-8')

    # Use a text loader to load the document
    loader = TextLoader(text)
    documents = loader.load()

    # Use a text splitter to split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

    for i, doc in enumerate(texts):
        vectorstore.add_texts([(doc, {"text": doc, "metadata": f"{file.filename}_{i}"})])

    return {"filename": file.filename, "message": "File uploaded and processed successfully."}

@app.post("/ask", response_model=Answer)
def ask_question(query: Query):
    embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

    context = vectorstore.similarity_search(query.question, k=5)

    # context = ' '.join([match['text'] for match in result])
    print(context)
    qa_result = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: {context}\n\nQuestion: {query.question}\n\nAnswer:",
        max_tokens=150
    )

    return Answer(answer=qa_result['choices'][0]['text'].strip())

# Run the app using: uvicorn main:app --reload
