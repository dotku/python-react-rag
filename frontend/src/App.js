import React, { useState } from "react";
import axios from "axios";
import "./App.css";
import { Button, Input } from "@nextui-org/react";
import ReactMarkdown from "react-markdown";

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
      const rsp = await axios.post(
        `${process.env.REACT_APP_FASTAPI_URL}/uploadfile/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(rsp);
      setAnswer(rsp.data.answer);
    } catch (error) {
      console.error("There was an error uploading the file!", error);
    }
  };

  return (
    <div className="App">
      <header className="App-header py-3">
        <h1>RAG System</h1>
      </header>
      <main className=" mx-auto py-5">
        <div className="w-96 mx-auto">
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
            <Input
              type="file"
              onChange={handleFileChange}
              accept=".txt,application/pdf"
            />
            <Button onClick={handleFileUpload} className="w-[100px]">
              Upload File
            </Button>
          </div>
        </div>
        <div className="max-w-5xl mx-auto">
          {answer && (
            <div className="answer text-left">
              <h2>Answer:</h2>
              <ReactMarkdown>{answer}</ReactMarkdown>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
