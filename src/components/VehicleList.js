import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';
import Poster from './VehiclePoster';

const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMsg, setRefreshMsg] = useState('');
  const [useDirectScrape, setUseDirectScrape] = useState(true);

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
    
    // Normalize CSV data
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
    
    // Check if response is ok
    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }
    
    // Check content type
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
    
    // Normalize API data to match CSV format
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

  // Initial load - try API first, fallback to CSV
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
        // Direct API call
        const vehicles = await loadFromAPI();
        setVehicles(vehicles);
        setRefreshMsg(`Successfully fetched ${vehicles.length} vehicles from live scraping`);
      } else {
        // GitHub Action trigger
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

  if (loading) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>Loading inventory...</p>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '8px' }}>
            {useDirectScrape ? 'Trying live scraping...' : 'Loading from CSV...'}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div style={{ 
          padding: '20px', 
          border: '2px solid #ff6b6b', 
          borderRadius: '8px', 
          background: '#fff5f5',
          margin: '20px 0'
        }}>
          <h3 style={{ color: '#d63031', margin: '0 0 10px 0' }}>Error Loading Data</h3>
          <p style={{ margin: '0 0 15px 0' }}>{error}</p>
          <button 
            className="btn" 
            onClick={() => window.location.reload()}
            style={{ marginRight: '10px' }}
          >
            Retry
          </button>
          <button 
            className="btn" 
            onClick={() => setUseDirectScrape(!useDirectScrape)}
          >
            Try {useDirectScrape ? 'CSV' : 'API'} Mode
          </button>
        </div>
      </div>
    );
  }

  if (!vehicles.length) {
    return (
      <div className="container">
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <h3>No Vehicles Available</h3>
          <p>No inventory data found. Try running the scraper to generate data.</p>
          <button className="btn" onClick={triggerRefresh}>
            Run Scraper Now
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Used Inventory Posters</h1>
      <p className="hint">Click "Download PDF" on any vehicle to generate a windshield poster.</p>
      
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        alignItems: 'center', 
        marginBottom: '20px', 
        flexWrap: 'wrap',
        padding: '12px',
        background: '#f8f9fa',
        borderRadius: '8px'
      }}>
        <button 
          className="btn" 
          onClick={triggerRefresh} 
          disabled={refreshing}
          style={{ 
            opacity: refreshing ? 0.6 : 1,
            cursor: refreshing ? 'not-allowed' : 'pointer'
          }}
        >
          {refreshing ? 'Working...' : 'Refresh Inventory'}
        </button>
        
        <label style={{ 
          display: 'inline-flex', 
          alignItems: 'center', 
          gap: '6px', 
          fontSize: '14px',
          cursor: 'pointer'
        }}>
          <input 
            type="checkbox" 
            checked={useDirectScrape} 
            onChange={(e) => setUseDirectScrape(e.target.checked)}
            disabled={refreshing}
          />
          Direct scrape (live data)
        </label>
        
        <div style={{ fontSize: '12px', color: '#666' }}>
          {vehicles.length} vehicles loaded
        </div>
        
        {refreshMsg && (
          <span style={{ 
            color: refreshMsg.startsWith('Error') ? '#d63031' : '#00b894', 
            fontWeight: '600',
            fontSize: '14px'
          }}>
            {refreshMsg}
          </span>
        )}
      </div>

      <div className="grid">
        {vehicles.map((vehicle, index) => (
          <div className="card" key={`${vehicle.stock_number || vehicle.model || index}-${index}`}>
            <Poster vehicle={vehicle} compact />
          </div>
        ))}
      </div>
    </div>
  );
};

export default VehicleList;
