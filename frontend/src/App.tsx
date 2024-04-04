import React, { useState } from "react";
import "./App.css";

import PdfIcon from "./asset/pdf.png";
import DocIcon from "./asset/doc.png";
import CsvIcon from "./asset/csv.png";
import TxtIcon from "./asset/txt.png";
import logo from "./asset/logo.svg";
import axios from "axios";

function App() {
  const [isUploaded, setIsUploaded] = useState(false);
  const [iconData, setIconData] = useState({
    name: "",
    type: "",
    secretname: "",
  });
  const [chatHistory, setChatHistory] = useState<
    { role: string; message: string }[]
  >([]);
  const [inputText, setInputText] = useState("");

  const icons: { [id: string]: string } = {
    pdf: PdfIcon,
    doc: DocIcon,
    docx: DocIcon,
    csv: CsvIcon,
    txt: TxtIcon,
  };

  const handleOnFileSelected = async (e: any) => {
    e.preventDefault();

    const file = e.target.files[0];
    if (file == null) {
      setIsUploaded(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const res = await axios.post("http://localhost:8000/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    const { filetype, filename } = res.data;

    setIconData({
      name: file.name,
      type: filetype,
      secretname: filename,
    });

    setIsUploaded(true);
  };

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    const response = await axios.post("http://localhost:8000/predict", {
      query: inputText,
      filename: iconData.secretname,
    });

    setChatHistory([
      ...chatHistory,
      {
        role: "user",
        message: inputText,
      },
      {
        role: "ai",
        message: response.data.result,
      },
    ]);
    setInputText("");
  };

  return (
    <div className="App">
      <aside className="sidebar">
        <div className="menu-title">Upload file</div>
        {isUploaded ? (
          <></>
        ) : (
          <div className="upload-button">
            <input
              type="file"
              placeholder="x"
              id="file"
              name="file"
              accept=".csv, .pdf, .doc, .docx, .txt"
              className="fileInput"
              onChange={handleOnFileSelected}
            />
          </div>
        )}

        {isUploaded ? (
          <div className="file-preview">
            <img
              className="file-icon"
              src={icons[iconData.type]}
              alt={iconData.type + " icon"}
            />
            {iconData.name}
          </div>
        ) : (
          <></>
        )}
      </aside>
      <section className="chatbox">
        {isUploaded ? (
          <>
            <div className="message-list">
              {chatHistory.map((chat, index) => (
                <div key={index} className={`chat-message ${chat.role}`}>
                  <div className="chat-message-center">
                    <div className={`avatar ${chat.role}`}>
                      {chat.role === "ai" ? (
                        <img src={logo} alt="logo" />
                      ) : (
                        <></>
                      )}
                    </div>
                    <div className="message">{chat.message}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="user-input-holder">
              <form onSubmit={handleSubmit}>
                <input
                  placeholder="Start typing..."
                  className="user-input-textarea"
                  value={inputText}
                  onChange={(e) => {
                    setInputText(e.target.value);
                  }}
                ></input>
              </form>
            </div>
          </>
        ) : (
          <center>Upload a file to start chat</center>
        )}
      </section>
    </div>
  );
}

export default App;
