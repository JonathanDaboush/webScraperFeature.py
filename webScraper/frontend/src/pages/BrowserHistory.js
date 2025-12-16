import React, { useState, useEffect } from 'react';
import { Chrome, RefreshCw, Clock, Globe } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function BrowserHistory() {
  const [history, setHistory] = useState([]);
  const [categories, setCategories] = useState([]);
  const [topDomains, setTopDomains] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [browserType, setBrowserType] = useState('chrome');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const [historyRes, categoriesRes, domainsRes] = await Promise.all([
        axios.get(`${API_URL}/browser-history`).catch(() => ({ data: [] })),
        axios.get(`${API_URL}/browser-history/categories`).catch(() => ({ data: [] })),
        axios.get(`${API_URL}/browser-history/domains`).catch(() => ({ data: [] }))
      ]);

      setHistory(historyRes.data);
      setCategories(categoriesRes.data);
      setTopDomains(domainsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading history:', error);
      setLoading(false);
    }
  };

  const analyzeBrowserHistory = async () => {
    try {
      setAnalyzing(true);
      await axios.post(`${API_URL}/browser-history/analyze`, { browser: browserType });
      await loadHistory();
      setAnalyzing(false);
    } catch (error) {
      console.error('Error analyzing browser history:', error);
      alert('Failed to analyze browser history. Make sure the browser is closed and try again.');
      setAnalyzing(false);
    }
  };

  return (
    <div className="browser-history">
      <div className="page-header">
        <div>
          <h1>Browser History</h1>
          <p>Analyze your browsing patterns and discover shopping interests</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <select
            className="search-input"
            value={browserType}
            onChange={(e) => setBrowserType(e.target.value)}
            style={{ width: '150px' }}
          >
            <option value="chrome">Chrome</option>
            <option value="firefox">Firefox</option>
            <option value="edge">Edge</option>
          </select>
          <button
            className="btn btn-primary"
            onClick={analyzeBrowserHistory}
            disabled={analyzing}
          >
            {analyzing ? (
              <>
                <RefreshCw size={20} className="spinning" />
                Analyzing...
              </>
            ) : (
              <>
                <Chrome size={20} />
                Analyze History
              </>
            )}
          </button>
        </div>
      </div>

      <div className="alert alert-info">
        <Chrome size={20} />
        <div>
          <strong>Privacy Notice:</strong> Your browser history is analyzed locally and never shared. 
          We only extract product-related URLs to help you discover deals.
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          <div className="grid-2">
            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Interest Categories</h2>
              </div>
              {categories.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categories}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categories.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  <Globe size={48} />
                  <h3>No categories yet</h3>
                  <p>Analyze your browser history to see interests</p>
                </div>
              )}
            </div>

            <div className="card">
              <div className="card-header">
                <h2 className="card-title">Most Visited Domains</h2>
              </div>
              {topDomains.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={topDomains}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="domain" angle={-45} textAnchor="end" height={100} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="visits" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="empty-state">
                  <Clock size={48} />
                  <h3>No domain data</h3>
                  <p>Analyze your history to see top sites</p>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h2 className="card-title">Recent Product URLs</h2>
            </div>
            {history.length > 0 ? (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Domain</th>
                      <th>Category</th>
                      <th>Last Visit</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history.slice(0, 50).map((item, idx) => (
                      <tr key={idx}>
                        <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {item.title}
                        </td>
                        <td>
                          <span className="badge badge-info">{item.domain}</span>
                        </td>
                        <td>{item.category || 'Uncategorized'}</td>
                        <td>{new Date(item.lastVisit).toLocaleDateString()}</td>
                        <td>
                          <button
                            className="btn btn-secondary"
                            style={{ padding: '6px 12px', fontSize: '12px' }}
                            onClick={() => window.open(item.url, '_blank')}
                          >
                            Visit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <Chrome size={48} />
                <h3>No history data</h3>
                <p>Click "Analyze History" to extract your browsing data</p>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default BrowserHistory;
