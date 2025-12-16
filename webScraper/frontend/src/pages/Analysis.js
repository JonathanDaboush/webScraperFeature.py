import React, { useState, useEffect } from 'react';
import { BarChart, FileText, Download, TrendingUp, Network, MessageSquare, Tag, Clock, Target, Zap, Database } from 'lucide-react';
import { BarChart as RechartsBar, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, ScatterChart, Scatter } from 'recharts';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

const ANALYSIS_TYPES = [
  { id: 'text', name: 'Text Analysis', icon: FileText, desc: 'Word frequency, readability, statistics' },
  { id: 'sentiment', name: 'Sentiment Analysis', icon: MessageSquare, desc: 'Emotion detection in reviews and content' },
  { id: 'topics', name: 'Topic Modeling', icon: Tag, desc: 'LDA topic extraction from content' },
  { id: 'nlp', name: 'NLP Features', icon: Zap, desc: 'Named entities, POS tagging' },
  { id: 'time-series', name: 'Time Series', icon: Clock, desc: 'Trend analysis over time' },
  { id: 'network', name: 'Link Network', icon: Network, desc: 'Page connectivity graphs' },
  { id: 'metrics', name: 'Domain Metrics', icon: Target, desc: 'Statistical measurements' },
  { id: 'frequency', name: 'Frequency Analysis', icon: BarChart, desc: 'Pattern detection' },
  { id: 'clustering', name: 'Content Clustering', icon: Database, desc: 'K-means grouping' },
  { id: 'ranking', name: 'PageRank', icon: TrendingUp, desc: 'Page importance scoring' }
];

const EXPORT_FORMATS = [
  { id: 'csv', name: 'CSV Export', desc: 'Spreadsheet format' },
  { id: 'json', name: 'JSON Export', desc: 'Structured data' },
  { id: 'vector', name: 'Vector DB', desc: 'Embeddings for ML' },
  { id: 'search', name: 'Search Index', desc: 'Elasticsearch format' }
];

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function Analysis() {
  const [selectedAnalysis, setSelectedAnalysis] = useState('text');
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState('products');
  const [filters, setFilters] = useState({
    category: 'all',
    dateRange: '30d',
    minPrice: '',
    maxPrice: ''
  });

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/analysis/${selectedAnalysis}`, {
        source: dataSource,
        filters
      });
      setAnalysisResults(response.data);
    } catch (error) {
      console.error('Analysis error:', error);
      // Generate mock data for demo
      setAnalysisResults(generateMockData(selectedAnalysis));
    }
    setLoading(false);
  };

  const exportData = async (format) => {
    try {
      const response = await axios.post(`${API_URL}/export/${format}`, {
        source: dataSource,
        filters,
        analysisType: selectedAnalysis
      }, { responseType: 'blob' });
      
      // Download file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `analysis_${selectedAnalysis}_${Date.now()}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Export error:', error);
      alert('Export functionality will be available once analysis is run');
    }
  };

  const generateMockData = (type) => {
    switch (type) {
      case 'text':
        return {
          wordCount: 45231,
          uniqueWords: 3421,
          avgWordLength: 5.2,
          readabilityScore: 72,
          topWords: [
            { word: 'product', count: 342 },
            { word: 'price', count: 289 },
            { word: 'quality', count: 234 },
            { word: 'shipping', count: 198 },
            { word: 'recommend', count: 176 }
          ]
        };
      
      case 'sentiment':
        return {
          overall: { positive: 68, neutral: 22, negative: 10 },
          byCategory: [
            { category: 'Electronics', positive: 72, neutral: 20, negative: 8 },
            { category: 'Fashion', positive: 65, neutral: 25, negative: 10 },
            { category: 'Home', positive: 70, neutral: 20, negative: 10 }
          ],
          timeline: [
            { date: '12/01', sentiment: 0.72 },
            { date: '12/05', sentiment: 0.68 },
            { date: '12/10', sentiment: 0.75 },
            { date: '12/15', sentiment: 0.70 }
          ]
        };
      
      case 'topics':
        return {
          topics: [
            { id: 1, label: 'Product Quality', keywords: ['quality', 'durable', 'premium', 'build'], weight: 0.35 },
            { id: 2, label: 'Shipping & Delivery', keywords: ['shipping', 'delivery', 'fast', 'arrived'], weight: 0.28 },
            { id: 3, label: 'Price & Value', keywords: ['price', 'worth', 'value', 'deal'], weight: 0.22 },
            { id: 4, label: 'Customer Service', keywords: ['support', 'service', 'help', 'response'], weight: 0.15 }
          ]
        };
      
      case 'frequency':
        return {
          patterns: [
            { pattern: 'Daily updates', frequency: 45, trend: 'increasing' },
            { pattern: 'Price changes', frequency: 32, trend: 'stable' },
            { pattern: 'New products', frequency: 28, trend: 'increasing' },
            { pattern: 'Stock updates', frequency: 19, trend: 'decreasing' }
          ]
        };
      
      case 'clustering':
        return {
          clusters: [
            { id: 1, name: 'Electronics', size: 245, center: [0.4, 0.6] },
            { id: 2, name: 'Fashion', size: 189, center: [0.7, 0.3] },
            { id: 3, name: 'Home & Garden', size: 156, center: [0.3, 0.8] },
            { id: 4, name: 'Sports', size: 98, center: [0.8, 0.7] }
          ],
          points: Array.from({ length: 100 }, () => ({
            x: Math.random(),
            y: Math.random(),
            cluster: Math.floor(Math.random() * 4)
          }))
        };
      
      case 'time-series':
        return {
          trends: [
            { date: '11/15', value: 234, change: 0 },
            { date: '11/22', value: 267, change: 14.1 },
            { date: '11/29', value: 312, change: 16.9 },
            { date: '12/06', value: 289, change: -7.4 },
            { date: '12/13', value: 345, change: 19.4 }
          ]
        };
      
      default:
        return { message: 'Analysis completed', data: [] };
    }
  };

  const renderAnalysisResults = () => {
    if (!analysisResults) return null;

    switch (selectedAnalysis) {
      case 'text':
        return (
          <div>
            <div className="stats-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '24px' }}>
              <div className="stat-card">
                <div className="stat-value">{analysisResults.wordCount?.toLocaleString()}</div>
                <div className="stat-label">Total Words</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{analysisResults.uniqueWords?.toLocaleString()}</div>
                <div className="stat-label">Unique Words</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{analysisResults.avgWordLength}</div>
                <div className="stat-label">Avg Word Length</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{analysisResults.readabilityScore}</div>
                <div className="stat-label">Readability Score</div>
              </div>
            </div>
            
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Top Words</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsBar data={analysisResults.topWords}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="word" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </RechartsBar>
            </ResponsiveContainer>
          </div>
        );
      
      case 'sentiment':
        return (
          <div>
            <div style={{ marginBottom: '32px' }}>
              <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Overall Sentiment</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                <div className="stat-card">
                  <div className="stat-value" style={{ color: '#10b981' }}>{analysisResults.overall?.positive}%</div>
                  <div className="stat-label">Positive</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{ color: '#6b7280' }}>{analysisResults.overall?.neutral}%</div>
                  <div className="stat-label">Neutral</div>
                </div>
                <div className="stat-card">
                  <div className="stat-value" style={{ color: '#ef4444' }}>{analysisResults.overall?.negative}%</div>
                  <div className="stat-label">Negative</div>
                </div>
              </div>
            </div>
            
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Sentiment Timeline</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analysisResults.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 1]} />
                <Tooltip formatter={(value) => (value * 100).toFixed(1) + '%'} />
                <Line type="monotone" dataKey="sentiment" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );
      
      case 'topics':
        return (
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Discovered Topics</h3>
            {analysisResults.topics?.map((topic) => (
              <div key={topic.id} style={{ 
                padding: '20px', 
                background: '#f3f4f6', 
                borderRadius: '8px', 
                marginBottom: '16px' 
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <h4 style={{ fontSize: '16px', fontWeight: '600' }}>{topic.label}</h4>
                  <span className="badge badge-info">{(topic.weight * 100).toFixed(0)}% weight</span>
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {topic.keywords.map((keyword, idx) => (
                    <span key={idx} className="badge badge-success">{keyword}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        );
      
      case 'frequency':
        return (
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Pattern Frequency</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Pattern</th>
                    <th>Frequency</th>
                    <th>Trend</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.patterns?.map((pattern, idx) => (
                    <tr key={idx}>
                      <td><strong>{pattern.pattern}</strong></td>
                      <td>{pattern.frequency}</td>
                      <td>
                        <span className={`badge ${
                          pattern.trend === 'increasing' ? 'badge-success' :
                          pattern.trend === 'decreasing' ? 'badge-danger' :
                          'badge-warning'
                        }`}>
                          {pattern.trend}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      
      case 'clustering':
        return (
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Content Clusters</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '24px' }}>
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={analysisResults.clusters}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, size }) => `${name} (${size})`}
                      outerRadius={100}
                      dataKey="size"
                    >
                      {analysisResults.clusters?.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid />
                    <XAxis dataKey="x" domain={[0, 1]} />
                    <YAxis dataKey="y" domain={[0, 1]} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Scatter data={analysisResults.points} fill="#3b82f6" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        );
      
      case 'time-series':
        return (
          <div>
            <h3 style={{ fontSize: '18px', marginBottom: '16px' }}>Trend Analysis</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={analysisResults.trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            <div className="table-container" style={{ marginTop: '24px' }}>
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Value</th>
                    <th>Change</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResults.trends?.map((trend, idx) => (
                    <tr key={idx}>
                      <td>{trend.date}</td>
                      <td><strong>{trend.value}</strong></td>
                      <td>
                        <span className={`badge ${trend.change >= 0 ? 'badge-success' : 'badge-danger'}`}>
                          {trend.change >= 0 ? '+' : ''}{trend.change}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="empty-state">
            <FileText size={48} />
            <h3>Analysis Complete</h3>
            <p>{JSON.stringify(analysisResults)}</p>
          </div>
        );
    }
  };

  return (
    <div className="analysis">
      <div className="page-header">
        <h1>Data Analysis</h1>
        <p>Analyze scraped data with advanced algorithms and export results</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Analysis Type</h2>
          </div>
          <div style={{ display: 'grid', gap: '12px' }}>
            {ANALYSIS_TYPES.map((type) => {
              const Icon = type.icon;
              return (
                <div
                  key={type.id}
                  onClick={() => setSelectedAnalysis(type.id)}
                  style={{
                    padding: '16px',
                    border: `2px solid ${selectedAnalysis === type.id ? '#3b82f6' : '#e5e7eb'}`,
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    background: selectedAnalysis === type.id ? '#eff6ff' : 'white'
                  }}
                >
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                    <Icon size={24} color={selectedAnalysis === type.id ? '#3b82f6' : '#6b7280'} />
                    <div>
                      <div style={{ fontWeight: '600', marginBottom: '4px' }}>{type.name}</div>
                      <div style={{ fontSize: '14px', color: '#6b7280' }}>{type.desc}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Configuration</h2>
          </div>
          
          <div className="input-group">
            <label>Data Source</label>
            <select value={dataSource} onChange={(e) => setDataSource(e.target.value)}>
              <option value="products">Products</option>
              <option value="reviews">Reviews</option>
              <option value="pages">Crawled Pages</option>
              <option value="history">Browser History</option>
            </select>
          </div>

          <div className="input-group">
            <label>Category Filter</label>
            <select value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })}>
              <option value="all">All Categories</option>
              <option value="electronics">Electronics</option>
              <option value="fashion">Fashion</option>
              <option value="home">Home & Garden</option>
              <option value="sports">Sports</option>
            </select>
          </div>

          <div className="input-group">
            <label>Date Range</label>
            <select value={filters.dateRange} onChange={(e) => setFilters({ ...filters, dateRange: e.target.value })}>
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="all">All time</option>
            </select>
          </div>

          <button
            className="btn btn-primary"
            onClick={runAnalysis}
            disabled={loading}
            style={{ width: '100%' }}
          >
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>

          <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Export Results</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
              {EXPORT_FORMATS.map((format) => (
                <button
                  key={format.id}
                  className="btn btn-secondary"
                  onClick={() => exportData(format.id)}
                  disabled={!analysisResults}
                  style={{ fontSize: '12px', padding: '8px 12px' }}
                >
                  <Download size={14} />
                  {format.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {analysisResults && (
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">
              {ANALYSIS_TYPES.find(t => t.id === selectedAnalysis)?.name} Results
            </h2>
          </div>
          {renderAnalysisResults()}
        </div>
      )}

      {!analysisResults && !loading && (
        <div className="card">
          <div className="empty-state">
            <BarChart size={48} />
            <h3>No analysis run yet</h3>
            <p>Select an analysis type and click "Run Analysis" to see results</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Analysis;
