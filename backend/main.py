import os

from openai import OpenAI
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
openAIClient = OpenAI()

# Define the model for request and response
class Query(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    contents = await file.read()

    # Check file type and use the appropriate loader
    if file.filename.endswith('.pdf'):
        with open(f"/tmp/{file.filename}", "wb") as f:
            f.write(contents)
        loader = PyPDFLoader(f"/tmp/{file.filename}")
    else:
        with open(f"/tmp/{file.filename}", "w") as f:
            f.write(contents.decode('utf-8'))
        loader = TextLoader(f"/tmp/{file.filename}")

    documents = loader.load()
    print(documents)

    # Use a text splitter to split the documents into chunks
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)


    embeddings = OpenAIEmbeddings(openai_api_key=openAIClient.api_key)

    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")


    for i, doc in enumerate(texts):
        vectorstore.add_texts([doc.page_content], [{"text": doc, "metadata": f"{file.filename}_{i}"}])

    return Answer(answer=f"File {file.filename} uploaded and processed successfully.")

@app.post("/ask", response_model=Answer)
def ask_question(query: Query):
    embeddings = OpenAIEmbeddings(openai_api_key=openAIClient.api_key)
    vectorstore = PineconeVectorStore(index, embeddings, text_key="text")

    context = vectorstore.similarity_search(query.question, k=5)
    print(context)
    # return Answer(answer="hello?")
    # context = ' '.join([match['text'] for match in result])

    context_text = ' '.join([match.page_content for match in context])
    print(context_text)
    completion = openAIClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
          {
              "role": "system",
              "content": context_text
          },
          {
              "role": "system",
              "content": "search content only from doc, if you can't find related content just ask for related doc upload"
          },
          {
              "role": "user",
              "content": query.question
          }
        ]
    )
    # qa_result = response['choices'][0]['message']['content']
    print(completion.choices[0].message.content)
    # return Answer(answer="hello 0001")
    return Answer(answer=completion.choices[0].message.content)

# Run the app using: uvicorn main:app --reload
