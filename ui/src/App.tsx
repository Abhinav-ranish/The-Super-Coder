import { useNavigate } from "react-router-dom";

function App() {
  const navigate = useNavigate();

  return (
    <div className="d-flex flex-column min-vh-100 justify-content-center align-items-center bg-dark text-light p-4">
      <h1 className="display-4 mb-4">✨ VibeCode Machine ✨</h1>

      <div className="d-flex flex-column gap-3 w-100" style={{ maxWidth: 400 }}>
        <button
          className="btn btn-primary"
          onClick={() => navigate("/build")}
        >
          ➕ Build New App
        </button>
        <button className="btn btn-success" onClick={() => navigate("/myapps")}>🛠 Manage Existing Apps</button>
        <button className="btn btn-warning">⚙️ Settings</button>
      </div>
    </div>
  );
}

export default App;
