import React, { useState, useEffect } from 'react';
import { Save, Plus, Trash2, RefreshCw } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Settings() {
  const [sources, setSources] = useState([]);
  const [settings, setSettings] = useState({
    scrapeInterval: 3600,
    maxConcurrent: 5,
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    enableNotifications: true,
    priceDropThreshold: 10
  });
  const [saving, setSaving] = useState(false);
  const [newSource, setNewSource] = useState({ name: '', url: '', type: 'amazon' });

  useEffect(() => {
    loadSettings();
    loadSources();
  }, []);

  const loadSettings = async () => {
    try {
      const response = await axios.get(`${API_URL}/settings`).catch(() => ({ data: null }));
      if (response.data) {
        setSettings(response.data);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const loadSources = async () => {
    try {
      const response = await axios.get(`${API_URL}/sources`).catch(() => ({ data: [] }));
      setSources(response.data);
    } catch (error) {
      console.error('Error loading sources:', error);
    }
  };

  const saveSettings = async () => {
    try {
      setSaving(true);
      await axios.put(`${API_URL}/settings`, settings);
      alert('Settings saved successfully!');
      setSaving(false);
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Failed to save settings');
      setSaving(false);
    }
  };

  const addSource = async () => {
    if (!newSource.name || !newSource.url) {
      alert('Please fill in all fields');
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/sources`, newSource);
      setSources([...sources, response.data]);
      setNewSource({ name: '', url: '', type: 'amazon' });
    } catch (error) {
      console.error('Error adding source:', error);
      alert('Failed to add source');
    }
  };

  const deleteSource = async (sourceId) => {
    if (!confirm('Are you sure you want to delete this source?')) return;

    try {
      await axios.delete(`${API_URL}/sources/${sourceId}`);
      setSources(sources.filter(s => s.id !== sourceId));
    } catch (error) {
      console.error('Error deleting source:', error);
      alert('Failed to delete source');
    }
  };

  const runScraperNow = async (sourceId) => {
    try {
      await axios.post(`${API_URL}/sources/${sourceId}/scrape`);
      alert('Scraper started! Check Products page for results.');
    } catch (error) {
      console.error('Error running scraper:', error);
      alert('Failed to start scraper');
    }
  };

  return (
    <div className="settings">
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure scraper settings and manage product sources</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">General Settings</h2>
          </div>

          <div className="input-group">
            <label>Scrape Interval (seconds)</label>
            <input
              type="number"
              value={settings.scrapeInterval}
              onChange={(e) => setSettings({ ...settings, scrapeInterval: parseInt(e.target.value) })}
              min="60"
              step="60"
            />
            <small style={{ color: '#6b7280', marginTop: '4px', display: 'block' }}>
              How often to check for price updates (minimum 60 seconds)
            </small>
          </div>

          <div className="input-group">
            <label>Max Concurrent Scrapers</label>
            <input
              type="number"
              value={settings.maxConcurrent}
              onChange={(e) => setSettings({ ...settings, maxConcurrent: parseInt(e.target.value) })}
              min="1"
              max="10"
            />
            <small style={{ color: '#6b7280', marginTop: '4px', display: 'block' }}>
              Number of products to scrape simultaneously
            </small>
          </div>

          <div className="input-group">
            <label>Price Drop Threshold (%)</label>
            <input
              type="number"
              value={settings.priceDropThreshold}
              onChange={(e) => setSettings({ ...settings, priceDropThreshold: parseInt(e.target.value) })}
              min="1"
              max="100"
            />
            <small style={{ color: '#6b7280', marginTop: '4px', display: 'block' }}>
              Minimum price drop percentage to trigger notifications
            </small>
          </div>

          <div className="input-group">
            <label>User Agent</label>
            <input
              type="text"
              value={settings.userAgent}
              onChange={(e) => setSettings({ ...settings, userAgent: e.target.value })}
            />
            <small style={{ color: '#6b7280', marginTop: '4px', display: 'block' }}>
              Browser identification string for web requests
            </small>
          </div>

          <div className="input-group">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="checkbox"
                checked={settings.enableNotifications}
                onChange={(e) => setSettings({ ...settings, enableNotifications: e.target.checked })}
              />
              Enable Price Drop Notifications
            </label>
          </div>

          <button
            className="btn btn-primary"
            onClick={saveSettings}
            disabled={saving}
          >
            {saving ? (
              <>
                <RefreshCw size={20} className="spinning" />
                Saving...
              </>
            ) : (
              <>
                <Save size={20} />
                Save Settings
              </>
            )}
          </button>
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Add Product Source</h2>
          </div>

          <div className="input-group">
            <label>Source Name</label>
            <input
              type="text"
              placeholder="e.g., Amazon Electronics"
              value={newSource.name}
              onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
            />
          </div>

          <div className="input-group">
            <label>Source URL</label>
            <input
              type="text"
              placeholder="https://www.amazon.com/..."
              value={newSource.url}
              onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
            />
          </div>

          <div className="input-group">
            <label>Source Type</label>
            <select
              value={newSource.type}
              onChange={(e) => setNewSource({ ...newSource, type: e.target.value })}
            >
              <option value="amazon">Amazon</option>
              <option value="ebay">eBay</option>
              <option value="walmart">Walmart</option>
              <option value="generic">Generic</option>
            </select>
          </div>

          <button
            className="btn btn-primary"
            onClick={addSource}
          >
            <Plus size={20} />
            Add Source
          </button>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Active Sources</h2>
        </div>
        {sources.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>URL</th>
                  <th>Status</th>
                  <th>Last Scrape</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sources.map((source) => (
                  <tr key={source.id}>
                    <td>
                      <strong>{source.name}</strong>
                    </td>
                    <td>
                      <span className="badge badge-info">{source.type}</span>
                    </td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {source.url}
                    </td>
                    <td>
                      {source.enabled ? (
                        <span className="badge badge-success">Active</span>
                      ) : (
                        <span className="badge badge-danger">Disabled</span>
                      )}
                    </td>
                    <td>
                      {source.lastScrape
                        ? new Date(source.lastScrape).toLocaleString()
                        : 'Never'}
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn btn-secondary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => runScraperNow(source.id)}
                        >
                          <RefreshCw size={14} />
                          Run Now
                        </button>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                          onClick={() => deleteSource(source.id)}
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-state">
            <Plus size={48} />
            <h3>No sources configured</h3>
            <p>Add your first product source to start tracking prices</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Settings;
