// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import App from "./App";
import BuildApp from "./pages/BuildApp";
import "bootstrap/dist/css/bootstrap.min.css";
import MyApps from "./pages/MyApps";



ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/build" element={<BuildApp />} />
        <Route path="/myapps" element={<MyApps />} /> {/* ✅ */}
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
