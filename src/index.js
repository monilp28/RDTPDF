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

const InventoryApp = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMake, setSelectedMake] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [sortBy, setSortBy] = useState('year-desc');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetch('/data/inventory.csv')
      .then(response => response.text())
      .then(data => {
        const rows = data.split('\n').slice(1);
        const parsed = rows.filter(row => row.trim()).map(row => {
          const cols = row.split(',');
          return {
            makeName: cols[0] || '',
            year: cols[1] || '',
            model: cols[2] || '',
            trim: cols[4] || '',
            mileage: cols[5] || '',
            value: cols[6] || '',
            saleValue: cols[7] || '',
            stockNumber: cols[8] || '',
            engine: cols[9] || '',
          };
        });
        setVehicles(parsed);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setLoading(false);
      });
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
        v.year.includes(searchLower) ||
        v.stockNumber.toLowerCase().includes(searchLower);
      
      const matchesMake = !selectedMake || v.makeName === selectedMake;
      const matchesYear = !selectedYear || v.year === selectedYear;
      
      return matchesSearch && matchesMake && matchesYear;
    });

    filtered.sort((a, b) => {
      switch(sortBy) {
        case 'year-desc': return b.year.localeCompare(a.year);
        case 'year-asc': return a.year.localeCompare(b.year);
        case 'price-asc': return (parseInt(a.value) || 999999) - (parseInt(b.value) || 999999);
        case 'price-desc': return (parseInt(b.value) || 0) - (parseInt(a.value) || 0);
        case 'mileage-asc': return (parseInt(a.mileage) || 999999) - (parseInt(b.mileage) || 999999);
        case 'make': return a.makeName.localeCompare(b.makeName);
        default: return 0;
      }
    });

    return filtered;
  }, [vehicles, searchTerm, selectedMake, selectedYear, sortBy]);

  const formatPrice = (price) => {
    if (!price) return 'Contact for Price';
    return '$' + parseInt(price).toLocaleString();
  };

  const formatMileage = (miles) => {
    if (!miles) return 'N/A';
    return parseInt(miles).toLocaleString() + ' km';
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
              <p className="text-sm text-slate-600">Vehicles Available</p>
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
              className="w-full pl-12 pr-4 py-3 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none"
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
                {(selectedMake || selectedYear) && (
                  <button
                    onClick={() => { setSearchTerm(''); setSelectedMake(''); setSelectedYear(''); }}
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
                  <select value={selectedMake} onChange={(e) => setSelectedMake(e.target.value)} className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none">
                    <option value="">All Makes</option>
                    {makes.map(make => <option key={make} value={make}>{make}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Year</label>
                  <select value={selectedYear} onChange={(e) => setSelectedYear(e.target.value)} className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none">
                    <option value="">All Years</option>
                    {years.map(year => <option key={year} value={year}>{year}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Sort By</label>
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none">
                    <option value="year-desc">Newest First</option>
                    <option value="year-asc">Oldest First</option>
                    <option value="price-asc">Price: Low to High</option>
                    <option value="price-desc">Price: High to Low</option>
                    <option value="mileage-asc">Mileage: Low to High</option>
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
            <div className="text-slate-300 mx-auto mb-4"><CarIcon /></div>
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No vehicles found</h3>
            <p className="text-slate-600">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSorted.map((vehicle, index) => (
              <div key={index} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                <div className="bg-gradient-to-r from-red-600 to-red-700 p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-white font-bold text-xl">{vehicle.year} {vehicle.makeName}</h3>
                      <p className="text-red-100 text-lg">{vehicle.model}</p>
                      {vehicle.trim && (
                        <span className="inline-block mt-1 px-3 py-1 bg-white/20 text-white text-sm rounded-full">{vehicle.trim}</span>
                      )}
                    </div>
                    {vehicle.stockNumber && (
                      <div className="bg-white/20 px-3 py-1 rounded-lg">
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
                      <div>
                        {vehicle.saleValue && vehicle.value && parseInt(vehicle.saleValue) < parseInt(vehicle.value) ? (
                          <div>
                            <span className="text-slate-400 line-through text-sm mr-2">{formatPrice(vehicle.value)}</span>
                            <span className="text-2xl font-bold text-green-600">{formatPrice(vehicle.saleValue)}</span>
                          </div>
                        ) : (
                          <span className="text-2xl font-bold text-slate-900">{formatPrice(vehicle.value || vehicle.saleValue)}</span>
                        )}
                      </div>
                    </div>
                  )}

                  {vehicle.mileage && (
                    <div className="flex items-center space-x-2 text-slate-700">
                      <div className="text-blue-600"><GaugeIcon /></div>
                      <span>{formatMileage(vehicle.mileage)}</span>
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
                  <button className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-3 rounded-lg transition-colors">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default InventoryApp;
