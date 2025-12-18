import logo from './logo.svg';
import React, { useMemo, useState, Suspense } from "react";
import "./App.css";
import { pagesML, pagesAnalysis, getPageBySlugML, getPageBySlugAnalysis } from "./pages/pages.config";

export default function App() {
  // Empty string = show the section menu, "ml" or "analysis" = show that section's pages
  const [selectedSection, setSelectedSection] = useState("");
  // Empty string = show the menu
  const [selectedSlug, setSelectedSlug] = useState("");

  // When a page is selected, build a lazy component from its loader
  const LazyPage = useMemo(() => {
    if (!selectedSlug || !selectedSection) return null;
    const getPageBySlug = selectedSection === "ml" ? getPageBySlugML : getPageBySlugAnalysis;
    const entry = getPageBySlug(selectedSlug);
    if (!entry) return null;
    // React.lazy needs a function returning a promise (our load() does that)
    return React.lazy(entry.load);
  }, [selectedSlug, selectedSection]);

  const handleBackToSection = () => setSelectedSlug("");
  const handleBackToSections = () => {
    setSelectedSlug("");
    setSelectedSection("");
  };

  // If a page is selected → render it with Back
  if (selectedSlug && LazyPage && selectedSection) {
    const getPageBySlug = selectedSection === "ml" ? getPageBySlugML : getPageBySlugAnalysis;
    const { title } = getPageBySlug(selectedSlug);
    return (
      <div className="App">
        <header className="App-header" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button onClick={handleBackToSection}>⬅ Back</button>
          <h1 style={{ margin: 0 }}>{title}</h1>
        </header>
        <main style={{ padding: 16 }}>
          <Suspense fallback={<div>Loading…</div>}>
            <LazyPage />
          </Suspense>
          <div style={{ marginTop: 16 }}>
            <button onClick={handleBackToSection}>⬅ Back to {selectedSection === "ml" ? "ML" : "Analysis"} Projects</button>
            <button onClick={handleBackToSections} style={{ marginLeft: 8 }}>⬅ Back to Sections</button>
          </div>
        </main>
      </div>
    );
  }

  // If a section is selected but no page → show pages for that section
  if (selectedSection && !selectedSlug) {
    const pages = selectedSection === "ml" ? pagesML : pagesAnalysis;
    const sectionTitle = selectedSection === "ml" ? "ML" : "Analysis";
    
    return (
      <div className="App">
        <header className="App-header" style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button onClick={handleBackToSections}>⬅ Back</button>
          <h1 style={{ margin: 0 }}>{sectionTitle} Projects</h1>
        </header>
        <main style={{ padding: 16 }}>
          {pages.map(({ title, slug }) => (
            <button
              key={slug}
              onClick={() => setSelectedSlug(slug)}
              style={{ display: "block", margin: "8px 0", padding: "12px", width: "200px" }}
            >
              {title}
            </button>
          ))}
        </main>
      </div>
    );
  }

  // Otherwise render the section selection menu
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Projects</h1>
      </header>
      <main style={{ padding: 16 }}>
        <h2>Choose a Section:</h2>
        <button
          onClick={() => setSelectedSection("ml")}
          style={{ display: "block", margin: "8px 0", padding: "16px", width: "200px", fontSize: "16px" }}
        >
          Machine Learning
        </button>
        <button
          onClick={() => setSelectedSection("analysis")}
          style={{ display: "block", margin: "8px 0", padding: "16px", width: "200px", fontSize: "16px" }}
        >
          Data Analysis
        </button>
      </main>
    </div>
  );
}

