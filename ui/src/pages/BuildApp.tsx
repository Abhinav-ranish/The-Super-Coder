import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

function BuildApp() {
  const navigate = useNavigate();

  const [idea, setIdea] = useState("");
  const [projectName, setProjectName] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [rawLogs, setRawLogs] = useState("");
  const [buildSuccess, setBuildSuccess] = useState(false);
  const [showLogs, setShowLogs] = useState(false); // NEW

  const handleSubmit = async () => {
    if (!idea || !projectName) {
      alert("Please fill out both the project name and app idea.");
      return;
    }

    setIsLoading(true);
    setRawLogs("");
    setShowLogs(false); // hide logs when starting fresh

    try {
      const response = await fetch("http://localhost:8000/generate_app/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ idea, stream: true, projectName }),
      });

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
      
        setRawLogs((prevLogs) => {
          const updatedLogs = prevLogs + text;
      
          // ✅ Check inside while streaming
          if (
            updatedLogs.toLowerCase().includes("✅ app ran successfully") ||
            updatedLogs.toLowerCase().includes("✅ app ran successfully after auto-fix")
          ) {
            setBuildSuccess(true);
          }
      
          return updatedLogs;
        });
      
        const logBox = document.getElementById("logBox");
        if (logBox) {
          logBox.scrollTop = logBox.scrollHeight;
        }
      }

    } catch (error) {
      alert("❌ Error connecting to server.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="d-flex flex-column min-vh-100 bg-dark text-light p-4">

      {/* Top Left Back Button */}
      <div className="mb-4">
        <button
          className="btn btn-secondary"
          onClick={() => navigate("/")}
        >
          🔙 Back to Home
        </button>
      </div>

      {/* Success Page */}
      {buildSuccess ? (
        <div className="d-flex flex-column justify-content-center align-items-center flex-grow-1 text-center">
          <h1 className="display-4 text-success mb-4">🎉 Build Successful!</h1>
          <p className="lead">Your app <strong>{projectName}</strong> has been created successfully.</p>
          <button
            className="btn btn-primary mt-4"
            onClick={() => navigate("/")}
          >
            🚀 Back to Home
          </button>
        </div>
      ) : (
        // Build Form
        <div className="d-flex flex-column justify-content-center align-items-center flex-grow-1">
          <h1 className="h2 mb-4">🛠 Build New App</h1>

          <input
            className="form-control mb-3"
            placeholder="Enter app/folder name..."
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            style={{ width: '100%', maxWidth: 600 }}
          />

          <textarea
            className="form-control mb-3"
            placeholder="Describe the app you want to build..."
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            rows={5}
            style={{ width: '100%', maxWidth: 600 }}
          />

          <button
            onClick={handleSubmit}
            className="btn btn-primary mb-3"
            disabled={isLoading}
          >
            {isLoading ? "Building..." : "🚀 Generate App"}
          </button>

          {/* Expand / Collapse Logs Button */}
          {rawLogs && (
            <button
              onClick={() => setShowLogs((prev) => !prev)}
              className="btn btn-outline-light mb-3"
              style={{ width: '100%', maxWidth: 600 }}
            >
              {showLogs ? "🔽 Hide Logs" : "🔼 Expand Logs"}
            </button>
          )}

          {/* Logs Section (only if expanded) */}
          {showLogs && (
            <pre
              id="logBox"
              className="bg-black text-white p-3 rounded"
              style={{ width: '100%', maxWidth: 600, height: 300, overflowY: 'auto' }}
            >
              {rawLogs}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

export default BuildApp;
