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

  useEffect(() => {
    const url = `${process.env.PUBLIC_URL || ''}/data/inventory.csv`;
    fetch(url, { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch CSV: ${res.status}`);
        return res.text();
      })
      .then((csvText) => {
        const { data, errors } = Papa.parse(csvText, { header: true, skipEmptyLines: true });
        if (errors && errors.length) {
          console.warn('CSV parse errors:', errors);
        }
        // Normalize fields
        const normalized = data.map((row) => ({
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
        setVehicles(normalized);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const triggerRefresh = async () => {
    try {
      setRefreshing(true);
      setRefreshMsg('');
      if (useDirectScrape) {
        // Directly call serverless Python function to scrape and return JSON
        const res = await fetch('/api/scrape');
        const data = await res.json();
        if (!res.ok || !data?.ok) throw new Error(data?.error || 'Scrape failed');
        // Transform to match CSV-normalized fields if needed
        const normalized = (data.vehicles || []).map((row) => ({
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
        setVehicles(normalized);
        setRefreshMsg(`Fetched ${normalized.length} vehicles`);
      } else {
        // Fallback: dispatch GitHub Action to run scraper and redeploy
        const res = await fetch('/api/trigger-scrape', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(process.env.REACT_APP_ACTION_SECRET ? { 'x-action-secret': process.env.REACT_APP_ACTION_SECRET } : {}),
          },
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) throw new Error(data?.error || 'Failed to dispatch');
        setRefreshMsg('Scrape triggered. Data will update after workflow completes.');
      }
    } catch (e) {
      setRefreshMsg(`Error: ${e.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) return <div className="container"><p>Loading inventory…</p></div>;
  if (error) return <div className="container error">Error: {error}</div>;
  if (!vehicles.length) return <div className="container"><p>No vehicles available yet. Run the scraper to generate inventory.csv.</p></div>;

  return (
    <div className="container">
      <h1>Used Inventory Posters</h1>
      <p className="hint">Click “Download PDF” on any vehicle to generate a windshield poster.</p>
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 12, flexWrap: 'wrap' }}>
        <button className="btn" onClick={triggerRefresh} disabled={refreshing}>
          {refreshing ? 'Triggering…' : 'Refresh Inventory'}
        </button>
        <label style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 14 }}>
          <input type="checkbox" checked={useDirectScrape} onChange={(e) => setUseDirectScrape(e.target.checked)} />
          Direct scrape (no GitHub)
        </label>
        {refreshMsg && <span style={{ color: refreshMsg.startsWith('Error') ? '#b91c1c' : '#065f46', fontWeight: 700 }}>{refreshMsg}</span>}
      </div>
      <div className="grid">
        {vehicles.map((v, i) => (
          <div className="card" key={`${v.stock_number || v.model || i}-${i}`}>
            <Poster vehicle={v} compact />
          </div>
        ))}
      </div>
    </div>
  );
};

export default VehicleList;
