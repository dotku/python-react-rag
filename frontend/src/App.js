import React, { useState } from "react";
import axios from "axios";
import "./App.css";

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
      <header className="App-header">
        <h1>RAG System</h1>
        <input
          type="text"
          value={question}
          onChange={handleQuestionChange}
          placeholder="Ask a question..."
        />
        <button onClick={handleAsk}>Ask</button>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleFileUpload}>Upload File</button>
        {answer && (
          <div className="answer">
            <h2>Answer:</h2>
            <p>{answer}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
