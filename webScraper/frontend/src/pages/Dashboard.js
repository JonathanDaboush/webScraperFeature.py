import React, { useState, useEffect } from 'react';
import { TrendingDown, ShoppingCart, DollarSign, Activity } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Dashboard() {
  const [stats, setStats] = useState({
    totalProducts: 0,
    activeDeals: 0,
    avgSavings: 0,
    productsTracked: 0
  });
  
  const [recentDeals, setRecentDeals] = useState([]);
  const [priceData, setPriceData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load stats
      const statsRes = await axios.get(`${API_URL}/stats`).catch(() => ({ data: null }));
      if (statsRes.data) {
        setStats(statsRes.data);
      }
      
      // Load recent deals
      const dealsRes = await axios.get(`${API_URL}/deals?limit=5`).catch(() => ({ data: [] }));
      setRecentDeals(dealsRes.data);
      
      // Load price trend data
      const trendRes = await axios.get(`${API_URL}/price-trends`).catch(() => ({ data: [] }));
      setPriceData(trendRes.data);
      
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard:', error);
      setLoading(false);
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
    <div className="dashboard">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Overview of your product tracking and price monitoring</p>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-value">{stats.totalProducts}</div>
              <div className="stat-label">Total Products</div>
            </div>
            <div className="stat-icon blue">
              <ShoppingCart size={24} />
            </div>
          </div>
          <div className="stat-change positive">+12% from last month</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-value">{stats.activeDeals}</div>
              <div className="stat-label">Active Deals</div>
            </div>
            <div className="stat-icon green">
              <TrendingDown size={24} />
            </div>
          </div>
          <div className="stat-change positive">+{stats.activeDeals} new this week</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-value">${stats.avgSavings}</div>
              <div className="stat-label">Avg Savings</div>
            </div>
            <div className="stat-icon orange">
              <DollarSign size={24} />
            </div>
          </div>
          <div className="stat-change positive">+8% vs last month</div>
        </div>

        <div className="stat-card">
          <div className="stat-header">
            <div>
              <div className="stat-value">{stats.productsTracked}</div>
              <div className="stat-label">Being Tracked</div>
            </div>
            <div className="stat-icon purple">
              <Activity size={24} />
            </div>
          </div>
          <div className="stat-change positive">Active monitoring</div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Price Trends (7 Days)</h2>
          </div>
          {priceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={priceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="avgPrice" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="empty-state">
              <p>No price data available yet</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2 className="card-title">Recent Deals</h2>
          </div>
          {recentDeals.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Discount</th>
                    <th>Price</th>
                  </tr>
                </thead>
                <tbody>
                  {recentDeals.map((deal, idx) => (
                    <tr key={idx}>
                      <td>{deal.name}</td>
                      <td>
                        <span className="badge badge-success">
                          -{deal.discount}%
                        </span>
                      </td>
                      <td>${deal.currentPrice}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state">
              <TrendingDown size={48} />
              <h3>No deals found</h3>
              <p>Start tracking products to discover deals</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
