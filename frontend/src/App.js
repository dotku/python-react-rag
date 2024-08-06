import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import { Button, Input } from "@nextui-org/react";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [file, setFile] = useState(null);

  const handleQuestionChange = (e) => {
    setQuestion(e.target.value);
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleAsk = async () => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_FASTAPI_URL}/ask`,
        { question }
      );
      setAnswer(response.data.answer);
    } catch (error) {
      console.error("There was an error asking the question!", error);
    }
  };

  const handleFileUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post(
        `${process.env.REACT_APP_FASTAPI_URL}/uploadfile/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      alert("File uploaded and processed successfully.");
    } catch (error) {
      console.error("There was an error uploading the file!", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header py-3">
        <h1>RAG System</h1>
      </header>
      <main className="w-96 mx-auto py-5">
        <div className="flex gap-3 mb-3">
          <Input
            type="text"
            value={question}
            onChange={handleQuestionChange}
            placeholder="Ask a question..."
          />
          <Button onClick={handleAsk} color="primary" className="w-[100px]">
            Ask
          </Button>
        </div>
        <div className="flex gap-3 mb-3">
          <Input type="file" onChange={handleFileChange} />
          <Button onClick={handleFileUpload} className="w-[100px]">
            Upload File
          </Button>
        </div>
        {answer && (
          <div className="answer text-left">
            <h2>Answer:</h2>
            <p>{answer}</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
