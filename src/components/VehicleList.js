import React, { useEffect, useState } from 'react';
import Papa from 'papaparse';
import Poster from './VehiclePoster';

const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

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
          stock_number: row.stock_number || row.Stock || row.StockNumber || '',
          engine: row.engine || row.Engine || '',
        }));
        setVehicles(normalized);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="container"><p>Loading inventory…</p></div>;
  if (error) return <div className="container error">Error: {error}</div>;
  if (!vehicles.length) return <div className="container"><p>No vehicles available yet. Run the scraper to generate inventory.csv.</p></div>;

  return (
    <div className="container">
      <h1>Used Inventory Posters</h1>
      <p className="hint">Click “Download PDF” on any vehicle to generate a windshield poster.</p>
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
