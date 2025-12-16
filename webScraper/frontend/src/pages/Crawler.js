import React, { useState } from 'react';
import { Play, StopCircle, CheckCircle, XCircle, Clock, Globe, Download, BarChart2 } from 'lucide-react';

const API_URL = 'http://localhost:5000/api';

function Crawler() {
  const [crawling, setCrawling] = useState(false);
  const [url, setUrl] = useState('');
  const [keywords, setKeywords] = useState('');
  const [status, setStatus] = useState('');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const startCrawl = async () => {
    if (!url) {
      setError('Please enter a URL');
      return;
    }

    setCrawling(true);
    setError('');
    setStatus('Starting crawler...');
    setResult(null);

    try {
      const keywordArray = keywords.split(',').map(k => k.trim()).filter(k => k);
      
      setStatus('Fetching page...');
      const response = await fetch(`${API_URL}/crawl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: url,
          keywords: keywordArray
        })
      });

      const data = await response.json();

      if (response.ok) {
        setStatus('Crawl complete!');
        setResult(data);
      } else {
        setError(data.error || 'Crawl failed');
        setStatus('');
      }
    } catch (err) {
      setError('Connection failed. Is the backend running?');
      setStatus('');
    } finally {
      setCrawling(false);
    }
  };

  const stopCrawl = () => {
    setCrawling(false);
    setStatus('Stopped');
  };

  return (
    <div className="container py-4">
      <div className="mb-4">
        <h1 className="d-flex align-items-center gap-2 mb-2">
          <Globe size={28} /> Web Crawler
        </h1>
        <p className="text-muted">Crawl websites and extract structured data</p>
      </div>

      {/* Crawler Control */}
      <div className="card shadow-sm mb-4">
        <div className="card-body">
          <div className="mb-3">
            <label className="form-label fw-bold">URL to Crawl</label>
            <input
              type="text"
              className="form-control"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.python.org"
              disabled={crawling}
            />
          </div>

          <div className="mb-3">
            <label className="form-label fw-bold">Keywords (optional)</label>
            <input
              type="text"
              className="form-control"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="python, programming, tutorial"
              disabled={crawling}
            />
          </div>

          <div className="d-flex gap-2 mb-3">
            {!crawling ? (
              <button className="btn btn-primary d-flex align-items-center gap-2" onClick={startCrawl}>
                <Play size={18} /> Start Crawl
              </button>
            ) : (
              <button className="btn btn-danger d-flex align-items-center gap-2" onClick={stopCrawl}>
                <StopCircle size={18} /> Stop
              </button>
            )}
          </div>

          {status && (
            <div className={`alert ${crawling ? 'alert-info' : 'alert-success'} d-flex align-items-center gap-2 mb-0`}>
              {crawling ? <Clock size={16} /> : <CheckCircle size={16} />}
              {status}
            </div>
          )}

          {error && (
            <div className="alert alert-danger d-flex align-items-center gap-2 mb-0">
              <XCircle size={16} /> {error}
            </div>
          )}
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="card shadow-sm mb-4">
          <div className="card-header bg-success text-white d-flex align-items-center gap-2">
            <CheckCircle size={20} />
            <h5 className="mb-0">Crawl Complete</h5>
          </div>
          <div className="card-body">
            <div className="row g-3 mb-4">
              <div className="col-md-6">
                <label className="text-muted small">Title</label>
                <p className="mb-0 fw-semibold">{result.title || 'N/A'}</p>
              </div>

              <div className="col-md-6">
                <label className="text-muted small">URL</label>
                <p className="mb-0 text-break small">{result.url}</p>
              </div>

              <div className="col-md-6">
                <label className="text-muted small">Keywords</label>
                <p className="mb-0 fs-4 fw-bold text-primary">{result.keywords ? Object.values(result.keywords).flat().length : 0}</p>
              </div>

              <div className="col-md-6">
                <label className="text-muted small">Links</label>
                <p className="mb-0 fs-4 fw-bold text-primary">{result.links ? result.links.length : 0}</p>
              </div>
            </div>

            {result.keywords && Object.keys(result.keywords).length > 0 && (
              <div className="border-top pt-4">
                <h5 className="d-flex align-items-center gap-2 mb-3">
                  <BarChart2 size={20} /> Extracted Keywords
                </h5>
                {Object.entries(result.keywords).map(([category, words]) => (
                  words.length > 0 && (
                    <div key={category} className="mb-3">
                      <h6 className="text-capitalize mb-2">{category}</h6>
                      <div className="d-flex flex-wrap gap-2">
                        {words.slice(0, 10).map((word, idx) => (
                          <span key={idx} className="badge bg-primary">{word}</span>
                        ))}
                        {words.length > 10 && <span className="badge bg-secondary">+{words.length - 10} more</span>}
                      </div>
                    </div>
                  )
                ))}
              </div>
            )}

            <div className="d-flex gap-2 border-top pt-3 mt-3">
              <button className="btn btn-secondary" onClick={() => setResult(null)}>
                Clear Results
              </button>
              <button className="btn btn-primary d-flex align-items-center gap-2">
                <Download size={16} /> Export Data
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="card shadow-sm">
        <div className="card-body">
          <h5 className="card-title">Quick Tips</h5>
          <ul className="mb-0">
            <li>✅ Pre-approved sites: theatrecalgary.com, toyota.ca, imdb.com</li>
            <li>🤖 Respects robots.txt and rate limits automatically</li>
            <li>💾 Data saved to database automatically</li>
            <li>⚡ Use keywords to focus on specific topics</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default Crawler;
