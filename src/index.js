import React, { useState, useEffect, useMemo } from 'react';
import { Search, Car, DollarSign, Gauge, Package, Filter, X } from 'lucide-react';

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
        const parsed = rows
          .filter(row => row.trim())
          .map(row => {
            const cols = row.split(',');
            return {
              makeName: cols[0]?.trim() || '',
              year: cols[1]?.trim() || '',
              model: cols[2]?.trim() || '',
              subModel: cols[3]?.trim() || '',
              trim: cols[4]?.trim() || '',
              mileage: cols[5]?.trim() || '',
              value: cols[6]?.trim() || '',
              saleValue: cols[7]?.trim() || '',
              stockNumber: cols[8]?.trim() || '',
              engine: cols[9]?.trim() || '',
            };
          });
        setVehicles(parsed);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading inventory:', err);
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
    return `$${parseInt(price).toLocaleString()}`;
  };

  const formatMileage = (miles) => {
    if (!miles) return 'N/A';
    return `${parseInt(miles).toLocaleString()} km`;
  };

  const clearFilters = () => {
    setSearchTerm('');
    setSelectedMake('');
    setSelectedYear('');
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
      {/* Header */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Car className="w-8 h-8 text-red-600" />
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

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by make, model, trim, year, or stock number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none text-slate-900 placeholder-slate-400 transition-colors"
            />
          </div>

          {/* Filter Toggle Button */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
          >
            <Filter className="w-4 h-4" />
            <span className="font-medium">Filters</span>
            {(selectedMake || selectedYear) && (
              <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                {(selectedMake ? 1 : 0) + (selectedYear ? 1 : 0)}
              </span>
            )}
          </button>

          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-slate-50 rounded-lg border-2 border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold text-slate-900">Filter Options</h3>
                {(selectedMake || selectedYear) && (
                  <button
                    onClick={clearFilters}
                    className="text-sm text-red-600 hover:text-red-700 font-medium flex items-center space-x-1"
                  >
                    <X className="w-4 h-4" />
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
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none"
                  >
                    <option value="">All Makes</option>
                    {makes.map(make => (
                      <option key={make} value={make}>{make}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Year</label>
                  <select
                    value={selectedYear}
                    onChange={(e) => setSelectedYear(e.target.value)}
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none"
                  >
                    <option value="">All Years</option>
                    {years.map(year => (
                      <option key={year} value={year}>{year}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Sort By</label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-4 py-2 border-2 border-slate-200 rounded-lg focus:border-red-500 focus:outline-none"
                  >
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

      {/* Vehicle Grid */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {filteredAndSorted.length === 0 ? (
          <div className="text-center py-16">
            <Car className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">No vehicles found</h3>
            <p className="text-slate-600">Try adjusting your search or filters</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAndSorted.map((vehicle, index) => (
              <div
                key={index}
                className="bg-white rounded-xl shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
              >
                <div className="bg-gradient-to-r from-red-600 to-red-700 p-4">
                  <div className="flex items-start justify-between">
                    <div>
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
                      <DollarSign className="w-5 h-5 text-green-600" />
                      <div>
                        {vehicle.saleValue && vehicle.value && parseInt(vehicle.saleValue) < parseInt(vehicle.value) ? (
                          <div>
                            <span className="text-slate-400 line-through text-sm mr-2">
                              {formatPrice(vehicle.value)}
                            </span>
                            <span className="text-2xl font-bold text-green-600">
                              {formatPrice(vehicle.saleValue)}
                            </span>
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
                      <Gauge className="w-5 h-5 text-blue-600" />
                      <span>{formatMileage(vehicle.mileage)}</span>
                    </div>
                  )}

                  {vehicle.engine && (
                    <div className="flex items-center space-x-2 text-slate-700">
                      <Package className="w-5 h-5 text-orange-600" />
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
