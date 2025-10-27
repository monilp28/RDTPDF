import React, { useState, useEffect, useMemo } from 'react';

const SearchIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const CarIcon = () => (
  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17a2 2 0 11-4 0 2 2 0 014 0zM19 17a2 2 0 11-4 0 2 2 0 014 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0" />
  </svg>
);

const DollarIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const GaugeIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
  </svg>
);

const PackageIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
  </svg>
);

const FilterIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
  </svg>
);

const XIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
);

const RefreshIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
  </svg>
);

const InventoryApp = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMake, setSelectedMake] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [sortBy, setSortBy] = useState('year-desc');
  const [showFilters, setShowFilters] = useState(false);

  const loadInventory = () => {
    setLoading(true);
    setError(null);
    
    fetch('/data/inventory.csv')
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to load inventory data');
        }
        return response.text();
      })
      .then(data => {
        const rows = data.split('\n').slice(1); // Skip header row
        const parsed = rows
          .filter(row => row.trim())
          .map(row => {
            // Handle CSV with potential commas in quoted fields
            const cols = row.split(',').map(col => col.trim());
            return {
              makeName: cols[0] || '',
              year: cols[1] || '',
              model: cols[2] || '',
              subModel: cols[3] || '',
              trim: cols[4] || '',
              mileage: cols[5] || '',
              value: cols[6] || '',
              saleValue: cols[7] || '',
              stockNumber: cols[8] || '',
              engine: cols[9] || '',
            };
          })
          .filter(v => v.makeName && v.year); // Only include vehicles with at least make and year
        
        setVehicles(parsed);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading inventory:', err);
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadInventory();
  }, []);

  const makes = useMemo(() => 
    [...new Set(vehicles.map(v => v.makeName))].filter(Boolean).sort(),
    [vehicles]
  );

  const years = useMemo(() => 
    [...new Set(vehicles.map(v => v.year))].filter(Boolean).sort((a, b) => b - a),
    [vehicles]
  );

  const filteredAndSorted = useMemo(() => {
    let filtered = vehicles.filter(v => {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = !searchTerm || 
        v.makeName.toLowerCase().includes(searchLower) ||
        v.model.toLowerCase().includes(searchLower) ||
        v.trim.toLowerCase().includes(searchLower) ||
        v.subModel.toLowerCase().includes(searchLower) ||
        v.year.includes(searchLower) ||
        v.stockNumber.toLowerCase().includes(searchLower) ||
        v.engine.toLowerCase().includes(searchLower);
      
      const matchesMake = !selectedMake || v.makeName === selectedMake;
      const matchesYear = !selectedYear || v.year === selectedYear;
      
      return matchesSearch && matchesMake && matchesYear;
    });

    filtered.sort((a, b) => {
      switch(sortBy) {
        case 'year-desc': 
          return b.year.localeCompare(a.year);
        case 'year-asc': 
          return a.year.localeCompare(b.year);
        case 'price-asc': 
          return (parseInt(a.value || a.saleValue) || 999999) - (parseInt(b.value || b.saleValue) || 999999);
        case 'price-desc': 
          return (parseInt(b.value || b.saleValue) || 0) - (parseInt(a.value || a.saleValue) || 0);
        case 'mileage-asc': 
          return (parseInt(a.mileage) || 999999) - (parseInt(b.mileage) || 999999);
        case 'mileage-desc':
          return (parseInt(b.mileage) || 0) - (parseInt(a.mileage) || 0);
        case 'make': 
          return a.makeName.localeCompare(b.makeName);
        default: 
          return 0;
      }
    });

    return filtered;
  }, [vehicles, searchTerm, selectedMake, selectedYear, sortBy]);

  const formatPrice = (price) => {
    if (!price) return 'Contact for Price';
    const numPrice = parseInt(price);
    if (isNaN(numPrice)) return 'Contact for Price';
    return '$' + numPrice.toLocaleString();
  };

  const formatMileage = (miles) => {
    if (!miles) return 'N/A';
    const numMiles = parseInt(miles);
    if (isNaN(numMiles)) return 'N/A';
    return numMiles.toLocaleString() + ' km';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-red-600 border-t-transparent"></div>
          <p className="mt-4 text-slate-600 font-medium">Loading inventory...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="text-red-600 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-slate-900 mb-2">Failed to Load Inventory</h3>
          <p className="text-slate-600 mb-4">{error}</p>
          <button
            onClick={loadInventory}
            className="inline-flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
          >
            <RefreshIcon />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="text-red-600"><CarIcon /></div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Red Deer Toyota</h1>
                <p className="text-sm text-slate-600">Used Vehicle Inventory</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-red-600">{filteredAndSorted.length}</p>
              <p className="text-sm text-slate-600">
                {filteredAndSorted.length === vehicles.length 
                  ? 'Vehicles Available' 
                  : `of ${vehicles.length} Total`}
              </p>
            </div>
          </div>

          <div className="relative mb-4">
            <div className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400">
              <SearchIcon />
            </div>
            <input
              type="text"
              placeholder="Search by make, model, trim, year, or stock number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none transition-colors"
            />
          </div>

          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <FilterIcon />
            <span className="font-medium">Filters</span>
            {(selectedMake || selectedYear) && (
              <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                {(selectedMake ? 1 : 0) + (selectedYear ? 1 : 0)}
              </span>
            )}
          </button>

          {showFilters && (
            <div className="mt-4 p-4 bg-slate-50 rounded-lg border-2 border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-900">Filter Options</h3>
                {(selectedMake || selectedYear || searchTerm) && (
                  <button
                    onClick={() => { 
                      setSearchTerm(''); 
                      setSelectedMake(''); 
                      setSelectedYear(''); 
                    }}
                    className="text-sm text-red-600 hover:text-red-700 font-medium flex items-center space-x-1"
                  >
                    <XIcon />
                    <span>Clear All</span>
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Make</label>
                  <select 
                    value={selectedMake} 
                    onChange={(e) => setSelectedMake(e.target.value)} 
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none transition-colors"
                  >
                    <option value="">All Makes ({makes.length})</option>
                    {makes.map(make => (
                      <option key={make} value={make}>
                        {make} ({vehicles.filter(v => v.makeName === make).length})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Year</label>
                  <select 
                    value={selectedYear} 
                    onChange={(e) => setSelectedYear(e.target.value)} 
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none transition-colors"
                  >
                    <option value="">All Years ({years.length})</option>
                    {years.map(year => (
                      <option key={year} value={year}>
                        {year} ({vehicles.filter(v => v.year === year).length})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Sort By</label>
                  <select 
                    value={sortBy} 
                    onChange={(e) => setSortBy(e.target.value)} 
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none transition-colors"
                  >
                    <option value="year-desc">Newest First</option>
                    <option value="year-asc">Oldest First</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="mileage-asc">Mileage: Low to High</option>
                    <option value="mileage-desc">Mileage: High to Low</option>
                    <option value="make">Make (A-Z)</option>
                  </select>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {filteredAndSorted.length === 0 ? (
          <div className="text-center py-16">
            <div className="text-slate-300 mx-auto mb-4 flex justify-center"><CarIcon /></div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No vehicles found</h3>
            <p className="text-slate-600 mb-4">Try adjusting your search or filters</p>
            {(searchTerm || selectedMake || selectedYear) && (
              <button
                onClick={() => { 
                  setSearchTerm(''); 
                  setSelectedMake(''); 
                  setSelectedYear(''); 
                }}
                className="inline-flex items-center space-x-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition-colors"
              >
                <XIcon />
                <span>Clear Filters</span>
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSorted.map((vehicle, index) => (
              <div 
                key={`${vehicle.stockNumber || index}-${vehicle.year}-${vehicle.makeName}`} 
                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
              >
                <div className="bg-gradient-to-r from-red-600 to-red-700 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-white font-bold text-xl">
                        {vehicle.year} {vehicle.makeName}
                      </h3>
                      <p className="text-red-100 text-lg">{vehicle.model}</p>
                      {vehicle.trim && (
                        <span className="inline-block mt-1 px-3 py-1 bg-white/20 text-white text-sm rounded-full">
                          {vehicle.trim}
                        </span>
                      )}
                    </div>
                    {vehicle.stockNumber && (
                      <div className="bg-white/20 px-3 py-1 rounded-lg ml-2">
                        <p className="text-xs text-red-100">Stock</p>
                        <p className="text-white font-semibold text-sm">{vehicle.stockNumber}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-4 space-y-3">
                  {(vehicle.value || vehicle.saleValue) && (
                    <div className="flex items-center space-x-2">
                      <div className="text-green-600"><DollarIcon /></div>
                      <div className="flex-1">
                        {vehicle.saleValue && vehicle.value && parseInt(vehicle.saleValue) < parseInt(vehicle.value) ? (
                          <div>
                            <div className="text-slate-400 line-through text-sm">{formatPrice(vehicle.value)}</div>
                            <div className="text-2xl font-bold text-green-600">{formatPrice(vehicle.saleValue)}</div>
                            <div className="text-xs text-green-600 font-medium">
                              Save ${(parseInt(vehicle.value) - parseInt(vehicle.saleValue)).toLocaleString()}
                            </div>
                          </div>
                        ) : (
                          <span className="text-2xl font-bold text-slate-900">
                            {formatPrice(vehicle.value || vehicle.saleValue)}
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {vehicle.mileage && (
                    <div className="flex items-center space-x-2 text-slate-700">
                      <div className="text-blue-600"><GaugeIcon /></div>
                      <span className="font-medium">{formatMileage(vehicle.mileage)}</span>
                    </div>
                  )}

                  {vehicle.engine && (
                    <div className="flex items-center space-x-2 text-slate-700">
                      <div className="text-orange-600"><PackageIcon /></div>
                      <span className="text-sm">{vehicle.engine}</span>
                    </div>
                  )}
                </div>

                <div className="px-4 pb-4">
                  <button className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-lg transition-colors duration-200 transform hover:scale-105">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-slate-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <p className="text-slate-600 text-sm">
              © {new Date().getFullYear()} Red Deer Toyota. All rights reserved.
            </p>
            <button
              onClick={loadInventory}
              className="mt-4 md:mt-0 flex items-center space-x-2 text-slate-600 hover:text-red-600 transition-colors"
            >
              <RefreshIcon />
              <span className="text-sm font-medium">Refresh Inventory</span>
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default InventoryApp;
