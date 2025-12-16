import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, TrendingUp, History, ShoppingCart, Search, Settings, BarChart, Globe } from 'lucide-react';
import './App.css';

// Import pages
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import PriceTracker from './pages/PriceTracker';
import BrowserHistory from './pages/BrowserHistory';
import Research from './pages/Research';
import Analysis from './pages/Analysis';
import Crawler from './pages/Crawler';
import SettingsPage from './pages/Settings';

function Navigation() {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="sidebar">
      <div className="logo">
        <ShoppingCart size={32} />
        <h1>WebScraper</h1>
      </div>
      
      <ul className="nav-links">
        <li>
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            <Home size={20} />
            <span>Dashboard</span>
          </Link>
        </li>
        <li>
          <Link to="/products" className={isActive('/products') ? 'active' : ''}>
            <ShoppingCart size={20} />
            <span>Products</span>
          </Link>
        </li>
        <li>
          <Link to="/price-tracker" className={isActive('/price-tracker') ? 'active' : ''}>
            <TrendingUp size={20} />
            <span>Price Tracker</span>
          </Link>
        </li>
        <li>
          <Link to="/browser-history" className={isActive('/browser-history') ? 'active' : ''}>
            <History size={20} />
            <span>Browser History</span>
          </Link>
        </li>
        <li>
          <Link to="/research" className={isActive('/research') ? 'active' : ''}>
            <Search size={20} />
            <span>Research</span>
          </Link>
        </li>
        <li>
          <Link to="/crawler" className={isActive('/crawler') ? 'active' : ''}>
            <Globe size={20} />
            <span>Crawler</span>
          </Link>
        </li>
        <li>
          <Link to="/analysis" className={isActive('/analysis') ? 'active' : ''}>
            <BarChart size={20} />
            <span>Analysis</span>
          </Link>
        </li>
        <li>
          <Link to="/settings" className={isActive('/settings') ? 'active' : ''}>
            <Settings size={20} />
            <span>Settings</span>
          </Link>
        </li>
      </ul>
      
      <div className="nav-footer">
        <p>© 2025 WebScraper</p>
      </div>
    </nav>
  );
}

          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/price-tracker" element={<PriceTracker />} />
            <Route path="/browser-history" element={<BrowserHistory />} />
            <Route path="/research" element={<Research />} />
            <Route path="/crawler" element={<Crawler />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>path="/" element={<Dashboard />} />
            <Route path="/products" element={<Products />} />
            <Route path="/price-tracker" element={<PriceTracker />} />
            <Route path="/browser-history" element={<BrowserHistory />} />
            <Route path="/research" element={<Research />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
