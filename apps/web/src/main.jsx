import '@fontsource/cormorant-garamond/400.css';
import '@fontsource/cormorant-garamond/500.css';
import React from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App.jsx";
import "./styles.css";

const Root=import.meta.env.DEV && new URLSearchParams(location.search).get("inspect")==="opening"
 ? React.lazy(()=>import("./AnimationReview.jsx")) : App;
createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <React.Suspense fallback={null}><Root /></React.Suspense>
  </React.StrictMode>,
);
