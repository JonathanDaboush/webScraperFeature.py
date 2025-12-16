import React, { useState, useEffect } from 'react';
import { TrendingDown, Bell, LineChart as LineChartIcon, Filter } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function PriceTracker() {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [products, setProducts] = useState([]);
  const [priceHistory, setPriceHistory] = useState([]);
  const [priceDrops, setPriceDrops] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState('7d');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (selectedProduct) {
      loadPriceHistory(selectedProduct.id);
    }
  }, [selectedProduct, timeRange]);

  const loadData = async () => {
    try {
      const [productsRes, dropsRes, alertsRes] = await Promise.all([
        axios.get(`${API_URL}/products`).catch(() => ({ data: [] })),
        axios.get(`${API_URL}/price-drops?days=7`).catch(() => ({ data: [] })),
        axios.get(`${API_URL}/alerts`).catch(() => ({ data: [] }))
      ]);

      setProducts(productsRes.data);
      setPriceDrops(dropsRes.data);
      setAlerts(alertsRes.data);
      
      if (productsRes.data.length > 0) {
        setSelectedProduct(productsRes.data[0]);
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading data:', error);
      setLoading(false);
    }
  };

  const loadPriceHistory = async (productId) => {
    try {
      const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90;
      const response = await axios.get(`${API_URL}/products/${productId}/price-history?days=${days}`)
        .catch(() => ({ data: [] }));
      setPriceHistory(response.data);
    } catch (error) {
      console.error('Error loading price history:', error);
    }
  };

  const createAlert = async (productId, targetPrice) => {
    try {
      await axios.post(`${API_URL}/alerts`, { productId, targetPrice });
      loadData();
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="price-tracker">
      <div className="page-header">
        <h1>Price Tracker</h1>
        <p>Monitor price changes and set alerts for your tracked products</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Price Drops</h2>
          </div>
          {priceDrops.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Old Price</th>
                    <th>New Price</th>
                    <th>Savings</th>
                  </tr>
                </thead>
                <tbody>
                  {priceDrops.map((drop, idx) => (
                    <tr key={idx}>
                      <td>{drop.productName}</td>
                      <td style={{ textDecoration: 'line-through', color: '#6b7280' }}>
                        ${drop.oldPrice}
                      </td>
                      <td>
                        <strong>${drop.newPrice}</strong>
                      </td>
                      <td>
                        <span className="badge badge-success">
                          <TrendingDown size={12} />
                          ${drop.savings} ({drop.percentDrop}%)
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <TrendingDown size={48} />
              <h3>No recent price drops</h3>
              <p>We'll notify you when prices decrease</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Active Price Alerts</h2>
          </div>
          {alerts.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Current</th>
                    <th>Target</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.map((alert, idx) => (
                    <tr key={idx}>
                      <td>{alert.productName}</td>
                      <td>${alert.currentPrice}</td>
                      <td>${alert.targetPrice}</td>
                      <td>
                        {alert.triggered ? (
                          <span className="badge badge-success">Triggered</span>
                        ) : (
                          <span className="badge badge-warning">Waiting</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <Bell size={48} />
              <h3>No active alerts</h3>
              <p>Set price alerts to get notified of deals</p>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Price History</h2>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
            <select
              className="search-input"
              value={selectedProduct?.id || ''}
              onChange={(e) => {
                const product = products.find(p => p.id === parseInt(e.target.value));
                setSelectedProduct(product);
              }}
              style={{ width: '250px' }}
            >
              {products.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <select
              className="search-input"
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              style={{ width: '120px' }}
            >
              <option value="7d">7 Days</option>
              <option value="30d">30 Days</option>
              <option value="90d">90 Days</option>
            </select>
          </div>
        </div>
        {selectedProduct && priceHistory.length > 0 ? (
          <div>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip
                  formatter={(value) => `$${value}`}
                  labelStyle={{ color: '#1f2937' }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="price"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  name="Price"
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
            <div style={{ marginTop: '24px', padding: '16px', background: '#f3f4f6', borderRadius: '8px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                <div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Current Price</div>
                  <div style={{ fontSize: '20px', fontWeight: 'bold' }}>${selectedProduct.currentPrice}</div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Lowest Price</div>
                  <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#10b981' }}>
                    ${Math.min(...priceHistory.map(h => h.price)).toFixed(2)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Highest Price</div>
                  <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#ef4444' }}>
                    ${Math.max(...priceHistory.map(h => h.price)).toFixed(2)}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>Average Price</div>
                  <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                    ${(priceHistory.reduce((sum, h) => sum + h.price, 0) / priceHistory.length).toFixed(2)}
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-state">
            <LineChartIcon size={48} />
            <h3>No price history available</h3>
            <p>Price history will appear as we track this product</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default PriceTracker;
