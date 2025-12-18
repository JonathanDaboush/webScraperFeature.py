import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // State management
  const [activeTab, setActiveTab] = useState('generate')
  const [warehouses, setWarehouses] = useState([])
  const [currentWarehouse, setCurrentWarehouse] = useState(null)
  const [warehouseImage, setWarehouseImage] = useState(null)
  const [analysis, setAnalysis] = useState(null)
  const [systemStatus, setSystemStatus] = useState(null)
  const [trainingInfo, setTrainingInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  // Warehouse generation config
  const [config, setConfig] = useState({
    w: 16,
    h: 12,
    style: 'parallel',
    obstacle_prob: 0.03,
    min_aisle: 2,
    max_aisle: 3
  })

  // Load initial data
  useEffect(() => {
    loadWarehouses()
    loadSystemStatus()
    loadTrainingInfo()
  }, [])

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    try {
      setError('')
      const response = await fetch(`/api${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      if (!data.success) {
        throw new Error(data.error || 'API call failed')
      }
      
      return data
    } catch (err) {
      setError(err.message)
      throw err
    }
  }

  // Load warehouses list
  const loadWarehouses = async () => {
    try {
      const data = await apiCall('/warehouse/list')
      setWarehouses(data.warehouses || [])
    } catch (err) {
      console.error('Failed to load warehouses:', err)
    }
  }

  // Load system status
  const loadSystemStatus = async () => {
    try {
      const data = await apiCall('/system/status')
      setSystemStatus(data.status)
    } catch (err) {
      console.error('Failed to load system status:', err)
    }
  }

  // Load training info
  const loadTrainingInfo = async () => {
    try {
      const data = await apiCall('/training/info')
      setTrainingInfo(data.training_info)
    } catch (err) {
      console.error('Failed to load training info:', err)
    }
  }

  // Generate new warehouse
  const generateWarehouse = async () => {
    setLoading(true)
    try {
      const data = await apiCall('/warehouse/generate', {
        method: 'POST',
        body: JSON.stringify(config)
      })
      
      setCurrentWarehouse(data)
      setWarehouseImage(`data:image/png;base64,${data.image}`)
      setMessage(`Generated ${data.config.w}x${data.config.h} warehouse with ${data.tasks.length} sample tasks`)
      setAnalysis(null) // Clear previous analysis
    } catch (err) {
      console.error('Failed to generate warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Save warehouse
  const saveWarehouse = async () => {
    if (!currentWarehouse) {
      setError('No warehouse to save')
      return
    }

    const name = prompt('Enter warehouse name:')
    if (!name) return

    setLoading(true)
    try {
      const data = await apiCall('/warehouse/save', {
        method: 'POST',
        body: JSON.stringify({
          name: name,
          warehouse: currentWarehouse.warehouse,
          meta: currentWarehouse.meta,
          config: currentWarehouse.config
        })
      })
      
      setMessage(data.message)
      loadWarehouses() // Refresh list
    } catch (err) {
      console.error('Failed to save warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Load warehouse
  const loadWarehouse = async (warehouseName) => {
    setLoading(true)
    try {
      const data = await apiCall(`/warehouse/load/${warehouseName}`)
      
      setCurrentWarehouse(data.data)
      setWarehouseImage(`data:image/png;base64,${data.data.image}`)
      setMessage(`Loaded warehouse: ${warehouseName}`)
      setAnalysis(null) // Clear previous analysis
    } catch (err) {
      console.error('Failed to load warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Delete warehouse
  const deleteWarehouse = async (warehouseName) => {
    if (!confirm(`Are you sure you want to delete "${warehouseName}"?`)) return

    setLoading(true)
    try {
      const data = await apiCall(`/warehouse/delete/${warehouseName}`, {
        method: 'DELETE'
      })
      
      setMessage(data.message)
      loadWarehouses() // Refresh list
      
      // Clear current warehouse if it was deleted
      if (currentWarehouse && currentWarehouse.name === warehouseName) {
        setCurrentWarehouse(null)
        setWarehouseImage(null)
        setAnalysis(null)
      }
    } catch (err) {
      console.error('Failed to delete warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Analyze warehouse
  const analyzeWarehouse = async () => {
    if (!currentWarehouse) {
      setError('No warehouse to analyze')
      return
    }

    setLoading(true)
    try {
      const data = await apiCall('/warehouse/analyze', {
        method: 'POST',
        body: JSON.stringify({
          warehouse: currentWarehouse.warehouse
        })
      })
      
      setAnalysis(data.analysis)
      setMessage('Warehouse analysis completed')
    } catch (err) {
      console.error('Failed to analyze warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Export warehouse for training
  const exportWarehouse = async (warehouseName) => {
    setLoading(true)
    try {
      const data = await apiCall(`/warehouse/export/${warehouseName}`)
      
      // Download as JSON file
      const blob = new Blob([JSON.stringify(data.training_data, null, 2)], {
        type: 'application/json'
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${warehouseName}_training_data.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      setMessage(`Exported training data for ${warehouseName}`)
    } catch (err) {
      console.error('Failed to export warehouse:', err)
    } finally {
      setLoading(false)
    }
  }

  // Update config
  const updateConfig = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: field === 'style' ? value : Number(value)
    }))
  }

  // Clear messages
  const clearMessages = () => {
    setMessage('')
    setError('')
  }

  return (
    <div className="warehouse-app">
      {/* Header */}
      <header className="app-header">
        <h1>🏭 Warehouse Management System</h1>
        <div className="status-bar">
          {systemStatus && (
            <div className="status-indicators">
              <span className={`status-item ${systemStatus.warehouse_generation ? 'active' : 'inactive'}`}>
                📦 Generation
              </span>
              <span className={`status-item ${systemStatus.visualization ? 'active' : 'inactive'}`}>
                📊 Visualization
              </span>
              <span className={`status-item ${systemStatus.deep_learning ? 'active' : 'inactive'}`}>
                🤖 AI Training
              </span>
              <span className="status-item">
                💾 {systemStatus.saved_warehouses} Saved
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Navigation */}
      <nav className="tab-navigation">
        <button 
          className={activeTab === 'generate' ? 'active' : ''}
          onClick={() => setActiveTab('generate')}
        >
          🏗️ Generate
        </button>
        <button 
          className={activeTab === 'manage' ? 'active' : ''}
          onClick={() => setActiveTab('manage')}
        >
          📋 Manage
        </button>
        <button 
          className={activeTab === 'analyze' ? 'active' : ''}
          onClick={() => setActiveTab('analyze')}
        >
          📈 Analyze
        </button>
        <button 
          className={activeTab === 'training' ? 'active' : ''}
          onClick={() => setActiveTab('training')}
        >
          🤖 Training
        </button>
      </nav>

      {/* Messages */}
      {(message || error) && (
        <div className="message-bar">
          {message && <div className="message success">{message}</div>}
          {error && <div className="message error">{error}</div>}
          <button onClick={clearMessages} className="close-btn">×</button>
        </div>
      )}

      {/* Main Content */}
      <main className="main-content">
        {/* Generate Tab */}
        {activeTab === 'generate' && (
          <div className="tab-content">
            <div className="content-grid">
              <div className="config-panel">
                <h2>🏗️ Generate Warehouse</h2>
                
                <div className="config-form">
                  <div className="form-group">
                    <label>Width:</label>
                    <input 
                      type="number" 
                      min="6" 
                      max="30" 
                      value={config.w}
                      onChange={(e) => updateConfig('w', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Height:</label>
                    <input 
                      type="number" 
                      min="6" 
                      max="30" 
                      value={config.h}
                      onChange={(e) => updateConfig('h', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>Style:</label>
                    <select 
                      value={config.style}
                      onChange={(e) => updateConfig('style', e.target.value)}
                    >
                      <option value="parallel">Parallel Aisles</option>
                      <option value="block">Block Layout</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label>Obstacle Probability:</label>
                    <input 
                      type="range" 
                      min="0" 
                      max="0.1" 
                      step="0.005"
                      value={config.obstacle_prob}
                      onChange={(e) => updateConfig('obstacle_prob', e.target.value)}
                    />
                    <span>{(config.obstacle_prob * 100).toFixed(1)}%</span>
                  </div>
                  
                  <button 
                    onClick={generateWarehouse} 
                    disabled={loading}
                    className="primary-btn"
                  >
                    {loading ? '⏳ Generating...' : '🏗️ Generate Warehouse'}
                  </button>
                  
                  {currentWarehouse && (
                    <button 
                      onClick={saveWarehouse}
                      disabled={loading}
                      className="secondary-btn"
                    >
                      💾 Save Warehouse
                    </button>
                  )}
                </div>
              </div>
              
              <div className="visualization-panel">
                <h3>📊 Warehouse Layout</h3>
                {warehouseImage ? (
                  <div className="warehouse-display">
                    <img src={warehouseImage} alt="Warehouse Layout" />
                    {currentWarehouse && (
                      <div className="warehouse-info">
                        <p><strong>Size:</strong> {currentWarehouse.config.w} × {currentWarehouse.config.h}</p>
                        <p><strong>Style:</strong> {currentWarehouse.config.style}</p>
                        <p><strong>Tasks:</strong> {currentWarehouse.tasks.length}</p>
                        <p><strong>Generated:</strong> {new Date(currentWarehouse.timestamp).toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="placeholder">
                    <p>📋 Generate a warehouse to see the layout</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Manage Tab */}
        {activeTab === 'manage' && (
          <div className="tab-content">
            <h2>📋 Manage Warehouses</h2>
            
            <div className="warehouses-grid">
              {warehouses.length > 0 ? (
                warehouses.map((warehouse) => (
                  <div key={warehouse.name} className="warehouse-card">
                    <h3>{warehouse.name}</h3>
                    <div className="warehouse-details">
                      <p><strong>Size:</strong> {warehouse.size}</p>
                      <p><strong>Style:</strong> {warehouse.config.style || 'Unknown'}</p>
                      <p><strong>Created:</strong> {new Date(warehouse.timestamp).toLocaleDateString()}</p>
                    </div>
                    <div className="warehouse-actions">
                      <button 
                        onClick={() => loadWarehouse(warehouse.name)}
                        className="primary-btn small"
                      >
                        📂 Load
                      </button>
                      <button 
                        onClick={() => exportWarehouse(warehouse.name)}
                        className="secondary-btn small"
                      >
                        📤 Export
                      </button>
                      <button 
                        onClick={() => deleteWarehouse(warehouse.name)}
                        className="danger-btn small"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <p>📭 No saved warehouses found</p>
                  <p>Generate and save a warehouse to get started!</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <div className="tab-content">
            <h2>📈 Warehouse Analysis</h2>
            
            {currentWarehouse ? (
              <div className="analysis-content">
                <div className="current-warehouse">
                  <h3>Current Warehouse: {currentWarehouse.name || 'Generated'}</h3>
                  <button 
                    onClick={analyzeWarehouse}
                    disabled={loading}
                    className="primary-btn"
                  >
                    {loading ? '⏳ Analyzing...' : '📊 Analyze Efficiency'}
                  </button>
                </div>
                
                {analysis && (
                  <div className="analysis-results">
                    <div className="metrics-grid">
                      <div className="metric-card">
                        <h4>📏 Dimensions</h4>
                        <p>{analysis.dimensions.width} × {analysis.dimensions.height}</p>
                        <p>{analysis.dimensions.total_cells} total cells</p>
                      </div>
                      
                      <div className="metric-card">
                        <h4>📊 Cell Distribution</h4>
                        <div className="cell-stats">
                          <div>🟢 Free: {analysis.cell_counts.free} ({analysis.percentages.free.toFixed(1)}%)</div>
                          <div>⬛ Shelves: {analysis.cell_counts.shelves} ({analysis.percentages.shelves.toFixed(1)}%)</div>
                          <div>🔵 Drop Zones: {analysis.cell_counts.drop_zones} ({analysis.percentages.drop_zones.toFixed(1)}%)</div>
                          <div>🔴 Pickup Zones: {analysis.cell_counts.pickup_zones} ({analysis.percentages.pickup_zones.toFixed(1)}%)</div>
                          <div>🚫 Obstacles: {analysis.cell_counts.obstacles} ({analysis.percentages.obstacles.toFixed(1)}%)</div>
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <h4>⚡ Efficiency Metrics</h4>
                        <div className="efficiency-stats">
                          <div>📦 Storage Efficiency: {(analysis.efficiency_metrics.storage_efficiency * 100).toFixed(1)}%</div>
                          <div>🚶 Accessibility: {(analysis.efficiency_metrics.accessibility * 100).toFixed(1)}%</div>
                          <div>📏 Avg Task Distance: {analysis.efficiency_metrics.average_task_distance.toFixed(1)}</div>
                          <div>🏆 Overall Score: {analysis.efficiency_metrics.efficiency_score.toFixed(1)}/100</div>
                        </div>
                      </div>
                      
                      <div className="metric-card">
                        <h4>🎯 Task Analysis</h4>
                        <p>Sample Tasks: {analysis.sample_tasks}</p>
                        <p>Complexity Score: {analysis.complexity_score.toFixed(3)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <p>📋 No warehouse loaded for analysis</p>
                <p>Generate or load a warehouse first!</p>
              </div>
            )}
          </div>
        )}

        {/* Training Tab */}
        {activeTab === 'training' && (
          <div className="tab-content">
            <h2>🤖 AI Training Information</h2>
            
            {trainingInfo && (
              <div className="training-content">
                <div className="training-status">
                  <div className={`status-card ${trainingInfo.deep_learning_available ? 'available' : 'unavailable'}`}>
                    <h3>🧠 Deep Learning Status</h3>
                    <p className="status">
                      {trainingInfo.deep_learning_available ? '✅ Available' : '❌ Not Available'}
                    </p>
                    {!trainingInfo.deep_learning_available && (
                      <p className="reason">{trainingInfo.reason}</p>
                    )}
                  </div>
                </div>
                
                <div className="training-instructions">
                  <h3>📋 Training Instructions</h3>
                  <div className="instruction-steps">
                    {Object.entries(trainingInfo.instructions).map(([step, instruction]) => (
                      <div key={step} className="instruction-step">
                        <strong>{step}:</strong> <code>{instruction}</code>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="available-scripts">
                  <h3>🔧 Available Training Scripts</h3>
                  <ul className="scripts-list">
                    {trainingInfo.available_scripts.map((script, index) => (
                      <li key={index}><code>{script}</code></li>
                    ))}
                  </ul>
                </div>
                
                <div className="training-tips">
                  <h3>💡 Tips</h3>
                  <ul>
                    <li>Export warehouses from the Manage tab for training</li>
                    <li>Use <code>python test_system.py</code> to check your environment</li>
                    <li>Start with beginner_training.py for simple reinforcement learning</li>
                    <li>Use train_models.py for comprehensive AI training pipelines</li>
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>🏭 Warehouse Management System - AI-Powered Route Optimization</p>
        {systemStatus && (
          <p>System Status: {systemStatus.saved_warehouses} warehouses saved | 
             Last updated: {new Date(systemStatus.timestamp).toLocaleString()}</p>
        )}
      </footer>
    </div>
  )
}

export default App
