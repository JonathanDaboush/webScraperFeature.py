import React, { useState, useEffect } from 'react';
import { Search, Play, Clock, FileText, ExternalLink } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Research() {
  const [query, setQuery] = useState('');
  const [maxDepth, setMaxDepth] = useState(2);
  const [maxPages, setMaxPages] = useState(50);
  const [researching, setResearching] = useState(false);
  const [results, setResults] = useState(null);
  const [researchHistory, setResearchHistory] = useState([]);

  useEffect(() => {
    loadResearchHistory();
  }, []);

  const loadResearchHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/research/history`).catch(() => ({ data: [] }));
      setResearchHistory(response.data);
    } catch (error) {
      console.error('Error loading research history:', error);
    }
  };

  const startResearch = async () => {
    if (!query.trim()) {
      alert('Please enter a research query');
      return;
    }

    try {
      setResearching(true);
      setResults(null);
      
      const response = await axios.post(`${API_URL}/research/start`, {
        query,
        maxDepth,
        maxPages
      });

      setResults(response.data);
      loadResearchHistory();
      setResearching(false);
    } catch (error) {
      console.error('Error starting research:', error);
      alert('Failed to start research. Please try again.');
      setResearching(false);
    }
  };

  const viewResearch = async (researchId) => {
    try {
      const response = await axios.get(`${API_URL}/research/${researchId}`);
      setResults(response.data);
    } catch (error) {
      console.error('Error loading research:', error);
    }
  };

  return (
    <div className="research">
      <div className="page-header">
        <h1>Research</h1>
        <p>Automated web research to discover products and information</p>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Start New Research</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div className="input-group" style={{ marginBottom: 0 }}>
            <label>Research Query</label>
            <input
              type="text"
              placeholder="e.g., best wireless headphones under $200"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && startResearch()}
            />
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="input-group" style={{ marginBottom: 0 }}>
              <label>Max Depth (Links to Follow)</label>
              <input
                type="number"
                min="1"
                max="5"
                value={maxDepth}
                onChange={(e) => setMaxDepth(parseInt(e.target.value))}
              />
            </div>
            
            <div className="input-group" style={{ marginBottom: 0 }}>
              <label>Max Pages to Crawl</label>
              <input
                type="number"
                min="10"
                max="200"
                step="10"
                value={maxPages}
                onChange={(e) => setMaxPages(parseInt(e.target.value))}
              />
            </div>
          </div>

          <button
            className="btn btn-primary"
            onClick={startResearch}
            disabled={researching || !query.trim()}
            style={{ alignSelf: 'flex-start' }}
          >
            {researching ? (
              <>
                <Clock size={20} className="spinning" />
                Researching...
              </>
            ) : (
              <>
                <Play size={20} />
                Start Research
              </>
            )}
          </button>
        </div>
      </div>

      {researching && (
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
            <h3>Research in Progress</h3>
            <p style={{ color: '#6b7280' }}>
              This may take a few minutes depending on the depth and pages...
            </p>
          </div>
        </div>
      )}

      {results && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Research Results: {results.query}</h2>
            <span className="badge badge-success">
              {results.pagesFound} pages found
            </span>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Summary</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>{results.summary}</p>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Key Findings</h3>
            <ul style={{ paddingLeft: '20px' }}>
              {results.keyFindings?.map((finding, idx) => (
                <li key={idx} style={{ marginBottom: '8px', color: '#6b7280' }}>
                  {finding}
                </li>
              ))}
            </ul>
          </div>

          {results.productUrls && results.productUrls.length > 0 && (
            <div>
              <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Discovered Products</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>URL</th>
                      <th>Title</th>
                      <th>Source</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.productUrls.map((product, idx) => (
                      <tr key={idx}>
                        <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {product.url}
                        </td>
                        <td>{product.title}</td>
                        <td>
                          <span className="badge badge-info">{product.source}</span>
                        </td>
                        <td>
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                            onClick={() => window.open(product.url, '_blank')}
                          >
                            <ExternalLink size={14} />
                            Open
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Research History</h2>
        </div>
        {researchHistory.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Query</th>
                  <th>Pages Found</th>
                  <th>Date</th>
                  <th>Duration</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {researchHistory.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <strong>{item.query}</strong>
                    </td>
                    <td>{item.pagesFound}</td>
                    <td>{new Date(item.createdAt).toLocaleDateString()}</td>
                    <td>{item.duration}s</td>
                    <td>
                      <button
                        className="btn btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                        onClick={() => viewResearch(item.id)}
                      >
                        <FileText size={14} />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <Search size={48} />
            <h3>No research history</h3>
            <p>Start your first research to see results here</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Research;
