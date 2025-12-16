import React, { useState, useEffect } from 'react';
import { Search, Plus, TrendingDown, TrendingUp, ExternalLink } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function Products() {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  useEffect(() => {
    filterProducts();
  }, [searchTerm, categoryFilter, products]);

  const loadProducts = async () => {
    try {
      const response = await axios.get(`${API_URL}/products`).catch(() => ({ data: [] }));
      setProducts(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading products:', error);
      setLoading(false);
    }
  };

  const filterProducts = () => {
    let filtered = products;

    if (searchTerm) {
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.brand?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter(p => p.category === categoryFilter);
    }

    setFilteredProducts(filtered);
  };

  const getPriceChange = (product) => {
    if (!product.priceChange) return null;
    const change = product.priceChange;
    const isPositive = change > 0;
    return (
      <span className={`badge ${isPositive ? 'badge-danger' : 'badge-success'}`}>
        {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
        {Math.abs(change)}%
      </span>
    );
  };

  const categories = [...new Set(products.map(p => p.category))].filter(Boolean);

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="products">
      <div className="page-header">
        <div>
          <h1>Products</h1>
          <p>All tracked products across e-commerce sites</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          <Plus size={20} />
          Add Product
        </button>
      </div>

      <div className="card">
        <div className="search-bar">
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
            <input
              type="text"
              className="search-input"
              placeholder="Search products by name or brand..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{ paddingLeft: '44px' }}
            />
          </div>
          <select
            className="search-input"
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            style={{ width: '200px' }}
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Brand</th>
                <th>Category</th>
                <th>Current Price</th>
                <th>Change</th>
                <th>Source</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.length > 0 ? (
                filteredProducts.map((product) => (
                  <tr key={product.id}>
                    <td>
                      <strong>{product.name}</strong>
                    </td>
                    <td>{product.brand || '-'}</td>
                    <td>{product.category || '-'}</td>
                    <td>
                      <strong>${product.currentPrice?.toFixed(2)}</strong>
                      {product.originalPrice && product.originalPrice > product.currentPrice && (
                        <div style={{ fontSize: '12px', color: '#6b7280', textDecoration: 'line-through' }}>
                          ${product.originalPrice.toFixed(2)}
                        </div>
                      )}
                    </td>
                    <td>{getPriceChange(product)}</td>
                    <td>
                      <span className="badge badge-info">{product.source}</span>
                    </td>
                    <td>
                      <a
                        href={product.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-secondary"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                      >
                        <ExternalLink size={14} />
                        View
                      </a>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7">
                    <div className="empty-state">
                      <Search size={48} />
                      <h3>No products found</h3>
                      <p>Try adjusting your search or filters</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showAddModal && (
        <AddProductModal
          onClose={() => setShowAddModal(false)}
          onAdd={(newProduct) => {
            setProducts([...products, newProduct]);
            setShowAddModal(false);
          }}
        />
      )}
    </div>
  );
}

function AddProductModal({ onClose, onAdd }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAdd = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_URL}/products`, { url });
      onAdd(response.data);
    } catch (error) {
      console.error('Error adding product:', error);
      alert('Failed to add product. Please check the URL and try again.');
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        background: 'white',
        padding: '32px',
        borderRadius: '12px',
        maxWidth: '500px',
        width: '100%'
      }}>
        <h2 style={{ marginBottom: '24px' }}>Add Product to Track</h2>
        <div className="input-group">
          <label>Product URL</label>
          <input
            type="text"
            placeholder="https://www.amazon.com/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <small style={{ color: '#6b7280', marginTop: '8px', display: 'block' }}>
            Supports Amazon, eBay, and Walmart URLs
          </small>
        </div>
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary" onClick={onClose}>
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleAdd}
            disabled={!url || loading}
          >
            {loading ? 'Adding...' : 'Add Product'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Products;
