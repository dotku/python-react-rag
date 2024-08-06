import os
import pinecone
import openai
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Initialize Pinecone
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"), environment="us-west1-gcp")
index = pinecone.Index("rag-demo")

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
    sentences = text.split('.')

    for i, sentence in enumerate(sentences):
        response = openai.Embedding.create(input=sentence, model="text-embedding-ada-002")
        vector = response['data'][0]['embedding']
        index.upsert([(f"{file.filename}_{i}", vector)])

    return {"filename": file.filename, "message": "File uploaded and processed successfully."}

@app.post("/ask", response_model=Answer)
def ask_question(query: Query):
    # Get the embedding for the question
    response = openai.Embedding.create(input=query.question, model="text-embedding-ada-002")
    question_vector = response['data'][0]['embedding']

    # Get top 5 most relevant documents from Pinecone
    result = index.query(queries=[question_vector], top_k=5)

    context = ' '.join([match['metadata']['text'] for match in result['matches']])
    qa_result = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Context: {context}\n\nQuestion: {query.question}\n\nAnswer:",
        max_tokens=150
    )

    return Answer(answer=qa_result['choices'][0]['text'].strip())

# Run the app using: uvicorn main:app --reload
