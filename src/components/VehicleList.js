import React, { useEffect, useState, useMemo } from 'react';
import Papa from 'papaparse';
import Poster from './VehiclePoster';

const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMsg, setRefreshMsg] = useState('');
  const [useDirectScrape, setUseDirectScrape] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('all');

  // Function to load from CSV fallback
  const loadFromCSV = async () => {
    const url = `${process.env.PUBLIC_URL || ''}/data/inventory.csv`;
    const response = await fetch(url, { cache: 'no-store' });
    
    if (!response.ok) {
      throw new Error(`CSV not found (${response.status}). Run scraper first.`);
    }
    
    const csvText = await response.text();
    const { data, errors } = Papa.parse(csvText, { header: true, skipEmptyLines: true });
    
    if (errors && errors.length) {
      console.warn('CSV parse errors:', errors);
    }
    
    return data.map((row) => ({
      makeName: row.makeName || row.Make || '',
      year: row.year || row.Year || '',
      model: row.model || row.Model || '',
      'sub-model': row['sub-model'] || row.SubModel || row.Submodel || '',
      trim: row.trim || row.Trim || '',
      mileage: row.mileage || row.Mileage || '',
      value: row.value || row.Price || row.price || '',
      sale_value: row.sale_value || row.Sale || row.SalePrice || row.salePrice || '',
      stock_number: row.stock_number || row.Stock || row.StockNumber || '',
      engine: row.engine || row.Engine || '',
    }));
  };

  // Function to load from API
  const loadFromAPI = async () => {
    const response = await fetch('/api/scrape', {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Cache-Control': 'no-cache'
      }
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const text = await response.text();
      console.error('Non-JSON response received:', text.substring(0, 200));
      throw new Error(`Server returned HTML instead of JSON. Check server logs.`);
    }
    
    const data = await response.json();
    
    if (!data.ok && !data.success) {
      throw new Error(data.error || 'API returned error response');
    }
    
    return (data.vehicles || []).map((row) => ({
      makeName: row.makeName || '',
      year: row.year || '',
      model: row.model || '',
      'sub-model': row['sub-model'] || '',
      trim: row.trim || '',
      mileage: row.mileage || '',
      value: row.value || '',
      sale_value: row.sale_value || '',
      stock_number: row.stock_number || '',
      engine: row.engine || '',
    }));
  };

  // Initial load
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError('');
        
        let vehicles = [];
        let source = '';
        
        if (useDirectScrape) {
          try {
            vehicles = await loadFromAPI();
            source = 'API';
          } catch (apiError) {
            console.warn('API failed, trying CSV fallback:', apiError.message);
            try {
              vehicles = await loadFromCSV();
              source = 'CSV (API failed)';
            } catch (csvError) {
              throw new Error(`Both API and CSV failed. API: ${apiError.message}, CSV: ${csvError.message}`);
            }
          }
        } else {
          vehicles = await loadFromCSV();
          source = 'CSV';
        }
        
        setVehicles(vehicles);
        console.log(`Loaded ${vehicles.length} vehicles from ${source}`);
        
      } catch (err) {
        console.error('Load error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadInitialData();
  }, [useDirectScrape]);

  const triggerRefresh = async () => {
    try {
      setRefreshing(true);
      setRefreshMsg('');
      
      if (useDirectScrape) {
        const vehicles = await loadFromAPI();
        setVehicles(vehicles);
        setRefreshMsg(`Successfully fetched ${vehicles.length} vehicles from live scraping`);
      } else {
        const response = await fetch('/api/trigger-scrape', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(process.env.REACT_APP_ACTION_SECRET ? { 
              'x-action-secret': process.env.REACT_APP_ACTION_SECRET 
            } : {}),
          },
        });
        
        const data = await response.json().catch(() => ({}));
        
        if (!response.ok) {
          throw new Error(data?.error || `HTTP ${response.status}`);
        }
        
        setRefreshMsg('Scrape workflow triggered. Data will update after completion (~2-5 minutes).');
      }
      
    } catch (err) {
      console.error('Refresh error:', err);
      setRefreshMsg(`Error: ${err.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  // Get unique brands for filtering
  const brands = useMemo(() => {
    const brandSet = new Set(vehicles.map(v => v.makeName).filter(Boolean));
    return ['all', ...Array.from(brandSet).sort()];
  }, [vehicles]);

  // Filter and search vehicles
  const filteredVehicles = useMemo(() => {
    return vehicles.filter(vehicle => {
      // Brand filter
      if (selectedBrand !== 'all' && vehicle.makeName !== selectedBrand) {
        return false;
      }

      // Search filter
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const searchableText = [
          vehicle.makeName,
          vehicle.year,
          vehicle.model,
          vehicle.trim,
          vehicle['sub-model'],
          vehicle.stock_number
        ].filter(Boolean).join(' ').toLowerCase();
        
        return searchableText.includes(query);
      }

      return true;
    });
  }, [vehicles, searchQuery, selectedBrand]);

  if (loading) {
    return (
      <div className="app-wrapper">
        <div className="container">
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <h3>Loading Inventory...</h3>
            <p style={{ color: '#64748b', marginTop: '8px' }}>
              {useDirectScrape ? 'Fetching live data...' : 'Loading from CSV...'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-wrapper">
        <div className="container">
          <div className="error-container">
            <h3 className="error-title">⚠️ Error Loading Data</h3>
            <p className="error-message">{error}</p>
            <div className="error-actions">
              <button 
                className="btn" 
                onClick={() => window.location.reload()}
              >
                🔄 Retry
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => setUseDirectScrape(!useDirectScrape)}
              >
                Switch to {useDirectScrape ? 'CSV' : 'API'} Mode
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!vehicles.length) {
    return (
      <div className="app-wrapper">
        <div className="container">
          <div className="empty-container">
            <div style={{ fontSize: '64px', marginBottom: '20px' }}>🚗</div>
            <h3>No Vehicles Available</h3>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
              No inventory data found. Try running the scraper to generate data.
            </p>
            <button className="btn" onClick={triggerRefresh}>
              Run Scraper Now
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-wrapper">
      <div className="container">
        {/* Header Section */}
        <div className="app-header-section">
          <div className="header-content">
            <div className="header-left">
              <h1 className="app-title">🚗 Red Deer Toyota Inventory</h1>
              <p className="app-subtitle">
                Browse our selection and generate printable windshield posters
              </p>
            </div>
            <div className="header-stats">
              <div className="stat-badge">
                📊 {filteredVehicles.length} Vehicle{filteredVehicles.length !== 1 ? 's' : ''}
              </div>
              {filteredVehicles.length !== vehicles.length && (
                <div className="stat-badge" style={{ background: '#64748b' }}>
                  Total: {vehicles.length}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Controls Section */}
        <div className="controls-section">
          <div className="controls-grid">
            {/* Search Bar */}
            <div className="search-wrapper">
              <input
                type="text"
                className="search-input"
                placeholder="Search by make, model, year, trim, or stock number..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button 
                  className="clear-search"
                  onClick={() => setSearchQuery('')}
                  aria-label="Clear search"
                >
                  ✕
                </button>
              )}
              <span className="search-icon">🔍</span>
            </div>

            {/* Actions */}
            <div className="action-buttons">
              <button 
                className="btn" 
                onClick={triggerRefresh} 
                disabled={refreshing}
              >
                {refreshing ? '⏳ Working...' : '🔄 Refresh'}
              </button>
              
              <label className="mode-toggle">
                <input 
                  type="checkbox" 
                  checked={useDirectScrape} 
                  onChange={(e) => setUseDirectScrape(e.target.checked)}
                  disabled={refreshing}
                />
                <span>Live scraping</span>
              </label>
            </div>
          </div>

          {/* Brand Filters */}
          {brands.length > 2 && (
            <div className="filter-section">
              <div className="filter-buttons">
                {brands.map(brand => (
                  <button
                    key={brand}
                    className={`filter-chip ${selectedBrand === brand ? 'active' : ''}`}
                    onClick={() => setSelectedBrand(brand)}
                  >
                    {brand === 'all' ? 'All Brands' : brand}
                    {brand !== 'all' && ` (${vehicles.filter(v => v.makeName === brand).length})`}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Status Message */}
          {refreshMsg && (
            <div className={`status-message ${refreshMsg.startsWith('Error') ? 'error' : 'success'}`}>
              {refreshMsg}
            </div>
          )}
        </div>

        {/* No Results Message */}
        {filteredVehicles.length === 0 && vehicles.length > 0 && (
          <div className="empty-container">
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h3>No Vehicles Found</h3>
            <p style={{ color: '#64748b', marginBottom: '20px' }}>
              Try adjusting your search or filter criteria
            </p>
            <button 
              className="btn btn-secondary" 
              onClick={() => {
                setSearchQuery('');
                setSelectedBrand('all');
              }}
            >
              Clear All Filters
            </button>
          </div>
        )}

        {/* Vehicle Grid */}
        {filteredVehicles.length > 0 && (
          <div className="grid">
            {filteredVehicles.map((vehicle, index) => (
              <div className="card" key={`${vehicle.stock_number || vehicle.model || index}-${index}`}>
                <Poster vehicle={vehicle} compact />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default VehicleList;
