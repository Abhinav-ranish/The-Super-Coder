// src/pages/MyApps.tsx

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function MyApps() {
  const navigate = useNavigate();
  const [apps, setApps] = useState<{ name: string, created: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://localhost:8000/list_apps")
      .then((res) => res.json())
      .then((data) => {
        setApps(data.apps || []);
        setLoading(false);
      })      
      .catch((error) => {
        console.error("Failed to fetch apps:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="d-flex flex-column min-vh-100 bg-dark text-light p-4">
      
      {/* Top Back Button */}
      <div className="mb-4">
        <button
          className="btn btn-secondary"
          onClick={() => navigate("/")}
        >
          🔙 Back to Home
        </button>
      </div>

      <h1 className="h2 text-center mb-4">📂 My Apps</h1>

      {loading ? (
        <div className="text-center">
          <div className="spinner-border text-primary" role="status" />
        </div>
      ) : apps.length === 0 ? (
        <p className="text-center">No apps found. Build your first app!</p>
      ) : (
        <div className="d-flex flex-column align-items-center">
            {apps.map(({ name, created }) => (
              <div key={name} className="card bg-secondary text-light mb-3" style={{ width: '100%', maxWidth: 600 }}>
                <div className="card-body d-flex justify-content-between align-items-center">
                  <div>
                    <h5 className="card-title mb-1">{name}</h5>
                    <small className="text-light">📅 {created}</small>
                  </div>
                  <div className="d-flex gap-2">
                    <button
                      className="btn btn-outline-light"
                      onClick={() => window.open(`http://localhost:8000/download_app/${name}`)}
                    >
                      📦 Download
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={async () => {
                        if (window.confirm(`Are you sure you want to delete "${name}"?`)) {
                          try {
                            const res = await fetch(`http://localhost:8000/delete_app/${name}`, {
                              method: "DELETE",
                            });

                            if (res.ok) {
                              alert("✅ Delete successful!");
                              // Re-fetch app list after deletion
                              const updated = await fetch("http://localhost:8000/list_apps");
                              const updatedData = await updated.json();
                              setApps(updatedData.apps || []);
                            } else {
                              alert("❌ Delete failed!");
                            }
                          } catch (error) {
                            console.error("Failed to delete app:", error);
                            alert("❌ Error deleting app.");
                          }
                        }
                      }}
                    >
                      🗑 Delete
                    </button>

                  </div>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

export default MyApps;

