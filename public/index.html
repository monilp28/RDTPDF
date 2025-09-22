import React, { useState, useMemo } from 'react';
import { Search, Filter, Car, Calendar, Gauge, Fuel, DollarSign, Eye, Download, X } from 'lucide-react';

const VehicleInventoryApp = ({ inventoryData = [] }) => {
  // Use real inventory data from props
  const [vehicles] = useState(inventoryData);
  const [loading, setLoading] = useState(inventoryData.length === 0);
  const [error, setError] = useState(null);

  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    make: '',
    year: '',
    priceRange: '',
    fuelType: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [viewMode, setViewMode] = useState('grid');

  // Get unique values for filter dropdowns - handle empty data gracefully
  const uniqueMakes = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.make))].sort() : [];
  const uniqueYears = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.year))].sort((a, b) => b - a) : [];
  const uniqueFuelTypes = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.fuelType || v.fuel_type || 'Gasoline'))].sort() : [];

  // Filter and search logic - handle different data structures from scraper
  const filteredVehicles = useMemo(() => {
    if (!vehicles || vehicles.length === 0) return [];
    
    return vehicles.filter(vehicle => {
      const searchableText = `${vehicle.year} ${vehicle.make} ${vehicle.model} ${vehicle.trim || ''} ${vehicle.stock || vehicle.stock_number || ''}`.toLowerCase();
      const matchesSearch = searchTerm === '' || searchableText.includes(searchTerm.toLowerCase());

      const matchesMake = filters.make === '' || vehicle.make === filters.make;
      const matchesYear = filters.year === '' || vehicle.year.toString() === filters.year;
      const matchesFuelType = filters.fuelType === '' || 
        (vehicle.fuelType || vehicle.fuel_type || 'Gasoline') === filters.fuelType;
      
      const vehiclePrice = parseFloat(vehicle.price) || 0;
      const matchesPrice = filters.priceRange === '' || (() => {
        switch(filters.priceRange) {
          case 'under-30k': return vehiclePrice < 30000;
          case '30k-50k': return vehiclePrice >= 30000 && vehiclePrice < 50000;
          case '50k-70k': return vehiclePrice >= 50000 && vehiclePrice < 70000;
          case 'over-70k': return vehiclePrice >= 70000;
          default: return true;
        }
      })();

      return matchesSearch && matchesMake && matchesYear && matchesFuelType && matchesPrice;
    });
  }, [vehicles, searchTerm, filters]);

  const clearFilters = () => {
    setSearchTerm('');
    setFilters({
      make: '',
      year: '',
      priceRange: '',
      fuelType: ''
    });
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(price);
  };

  const generatePoster = (vehicle) => {
    // This would integrate with your existing poster generation logic
    console.log('Generating poster for:', vehicle);
    alert(`Poster generated for ${vehicle.year} ${vehicle.make} ${vehicle.model}!`);
  };

  const VehicleCard = ({ vehicle }) => {
    // Handle different data structures from scraper
    const stockNumber = vehicle.stock || vehicle.stock_number || vehicle.vin || 'N/A';
    const vehicleImage = vehicle.image || vehicle.image_url || vehicle.photo || 
      `https://via.placeholder.com/300x200/2d3748/ffffff?text=${encodeURIComponent(vehicle.make + ' ' + vehicle.model)}`;
    const mileageDisplay = vehicle.mileage || vehicle.miles || 'N/A';
    const engineDisplay = vehicle.engine || vehicle.engine_size || 'N/A';
    const transmissionDisplay = vehicle.transmission || vehicle.trans || 'Auto';
    const fuelDisplay = vehicle.fuelType || vehicle.fuel_type || 'Gasoline';
    const colorDisplay = vehicle.color || vehicle.exterior_color || 'N/A';
    const priceDisplay = parseFloat(vehicle.price) || 0;
    const oldPriceDisplay = vehicle.oldPrice || vehicle.original_price || vehicle.msrp || null;
    
    return (
      <div className="bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden border border-slate-100 group">
        <div className="relative overflow-hidden">
          <img 
            src={vehicleImage} 
            alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
            className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.target.src = `https://via.placeholder.com/300x200/2d3748/ffffff?text=${encodeURIComponent(vehicle.make + ' ' + vehicle.model)}`;
            }}
          />
          <div className="absolute top-3 right-3 bg-black/70 text-white px-3 py-1 rounded-full text-sm font-medium">
            #{stockNumber}
          </div>
          {oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay && (
            <div className="absolute top-3 left-3 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
              SALE
            </div>
          )}
        </div>
        
        <div className="p-6">
          <div className="mb-4">
            <h3 className="text-2xl font-bold text-slate-800 mb-1">
              {vehicle.year} {vehicle.make}
            </h3>
            <p className="text-xl font-semibold text-slate-600">
              {vehicle.model} {vehicle.trim || ''}
            </p>
            <p className="text-sm text-slate-500 mt-1">{colorDisplay}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="flex items-center gap-2 text-slate-600">
              <Gauge className="w-4 h-4" />
              <span className="text-sm">{mileageDisplay} {typeof mileageDisplay === 'number' ? 'mi' : ''}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <Car className="w-4 h-4" />
              <span className="text-sm">{engineDisplay}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <Fuel className="w-4 h-4" />
              <span className="text-sm">{fuelDisplay}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-600">
              <Calendar className="w-4 h-4" />
              <span className="text-sm">{transmissionDisplay}</span>
            </div>
          </div>

          <div className="mb-4">
            {oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay && (
              <p className="text-lg text-slate-400 line-through font-medium">
                {formatPrice(parseFloat(oldPriceDisplay))}
              </p>
            )}
            <p className={`text-3xl font-bold ${oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay ? 'text-red-600' : 'text-slate-800'}`}>
              {formatPrice(priceDisplay)}
            </p>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={() => setSelectedVehicle(vehicle)}
              className="flex-1 bg-slate-800 text-white py-3 px-4 rounded-xl font-semibold hover:bg-slate-700 transition-colors flex items-center justify-center gap-2"
            >
              <Eye className="w-4 h-4" />
              View Details
            </button>
            <button 
              onClick={() => generatePoster(vehicle)}
              className="bg-blue-600 text-white py-3 px-4 rounded-xl font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  const VehicleModal = ({ vehicle, onClose }) => {
    if (!vehicle) return null;
    
    // Handle different data structures from scraper
    const stockNumber = vehicle.stock || vehicle.stock_number || vehicle.vin || 'N/A';
    const vehicleImage = vehicle.image || vehicle.image_url || vehicle.photo || 
      `https://via.placeholder.com/300x200/2d3748/ffffff?text=${encodeURIComponent(vehicle.make + ' ' + vehicle.model)}`;
    const mileageDisplay = vehicle.mileage || vehicle.miles || 'N/A';
    const engineDisplay = vehicle.engine || vehicle.engine_size || 'N/A';
    const transmissionDisplay = vehicle.transmission || vehicle.trans || 'Auto';
    const fuelDisplay = vehicle.fuelType || vehicle.fuel_type || 'Gasoline';
    const colorDisplay = vehicle.color || vehicle.exterior_color || 'N/A';
    const priceDisplay = parseFloat(vehicle.price) || 0;
    const oldPriceDisplay = vehicle.oldPrice || vehicle.original_price || vehicle.msrp || null;
    
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          <div className="relative">
            <img 
              src={vehicleImage} 
              alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
              className="w-full h-64 object-cover"
              onError={(e) => {
                e.target.src = `https://via.placeholder.com/300x200/2d3748/ffffff?text=${encodeURIComponent(vehicle.make + ' ' + vehicle.model)}`;
              }}
            />
            <button 
              onClick={onClose}
              className="absolute top-4 right-4 bg-black/70 text-white p-2 rounded-full hover:bg-black/90 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
            {oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay && (
              <div className="absolute top-4 left-4 bg-red-500 text-white px-4 py-2 rounded-full font-bold">
                ON SALE
              </div>
            )}
          </div>
          
          <div className="p-8">
            <div className="mb-6">
              <h2 className="text-4xl font-bold text-slate-800 mb-2">
                {vehicle.year} {vehicle.make} {vehicle.model}
              </h2>
              <p className="text-2xl text-slate-600 mb-1">{vehicle.trim || ''}</p>
              <p className="text-lg text-slate-500">Stock #{stockNumber}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-xl font-semibold mb-4 text-slate-800">Vehicle Details</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-slate-600">Color:</span>
                    <span className="font-medium">{colorDisplay}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Mileage:</span>
                    <span className="font-medium">{mileageDisplay} {typeof mileageDisplay === 'number' ? 'miles' : ''}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Engine:</span>
                    <span className="font-medium">{engineDisplay}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Transmission:</span>
                    <span className="font-medium">{transmissionDisplay}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-600">Fuel Type:</span>
                    <span className="font-medium">{fuelDisplay}</span>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="text-xl font-semibold mb-4 text-slate-800">Pricing</h3>
                <div className="bg-slate-50 p-6 rounded-xl">
                  {oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay && (
                    <p className="text-2xl text-slate-400 line-through font-medium mb-2">
                      {formatPrice(parseFloat(oldPriceDisplay))}
                    </p>
                  )}
                  <p className={`text-4xl font-bold ${oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay ? 'text-red-600' : 'text-slate-800'}`}>
                    {formatPrice(priceDisplay)}
                  </p>
                  {oldPriceDisplay && parseFloat(oldPriceDisplay) > priceDisplay && (
                    <p className="text-lg text-green-600 font-semibold mt-2">
                      Save {formatPrice(parseFloat(oldPriceDisplay) - priceDisplay)}!
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button 
                onClick={() => generatePoster(vehicle)}
                className="flex-1 bg-blue-600 text-white py-4 px-6 rounded-xl text-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-3"
              >
                <Download className="w-5 h-5" />
                Generate Poster
              </button>
              <button 
                onClick={onClose}
                className="px-6 py-4 border border-slate-300 text-slate-700 rounded-xl text-lg font-semibold hover:bg-slate-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <div className="bg-white shadow-lg border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center gap-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-slate-800 mb-2">Vehicle Inventory</h1>
              <p className="text-slate-600">Find and generate posters for our available vehicles</p>
            </div>
            
            {/* Search Bar */}
            <div className="flex-1 max-w-2xl">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search by make, model, year, or stock number..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-4 py-4 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                />
              </div>
            </div>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-6 py-4 bg-slate-800 text-white rounded-xl font-semibold hover:bg-slate-700 transition-colors"
            >
              <Filter className="w-5 h-5" />
              Filters
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="bg-white border-b border-slate-200 shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <select
                value={filters.make}
                onChange={(e) => setFilters({...filters, make: e.target.value})}
                className="px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Makes</option>
                {uniqueMakes.map(make => (
                  <option key={make} value={make}>{make}</option>
                ))}
              </select>

              <select
                value={filters.year}
                onChange={(e) => setFilters({...filters, year: e.target.value})}
                className="px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Years</option>
                {uniqueYears.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>

              <select
                value={filters.priceRange}
                onChange={(e) => setFilters({...filters, priceRange: e.target.value})}
                className="px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Prices</option>
                <option value="under-30k">Under $30,000</option>
                <option value="30k-50k">$30,000 - $50,000</option>
                <option value="50k-70k">$50,000 - $70,000</option>
                <option value="over-70k">Over $70,000</option>
              </select>

              <select
                value={filters.fuelType}
                onChange={(e) => setFilters({...filters, fuelType: e.target.value})}
                className="px-4 py-3 border border-slate-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Fuel Types</option>
                {uniqueFuelTypes.map(fuel => (
                  <option key={fuel} value={fuel}>{fuel}</option>
                ))}
              </select>
            </div>

            <button
              onClick={clearFilters}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 font-medium"
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-between mb-6">
          <p className="text-lg text-slate-600">
            {loading ? 'Loading inventory...' : `Showing ${filteredVehicles.length} of ${vehicles.length} vehicles`}
          </p>
        </div>

        {loading ? (
          <div className="text-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-slate-500">Loading vehicle inventory...</p>
          </div>
        ) : vehicles.length === 0 ? (
          <div className="text-center py-16">
            <Car className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-600 mb-2">No inventory data found</h3>
            <p className="text-slate-500">Please run your toyota_scrapper.py to populate the inventory</p>
          </div>
        ) : filteredVehicles.length === 0 ? (
          <div className="text-center py-16">
            <Car className="w-16 h-16 text-slate-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-600 mb-2">No vehicles found</h3>
            <p className="text-slate-500">Try adjusting your search or filter criteria</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredVehicles.map((vehicle, index) => (
              <VehicleCard key={vehicle.id || vehicle.stock || vehicle.stock_number || index} vehicle={vehicle} />
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      <VehicleModal 
        vehicle={selectedVehicle} 
        onClose={() => setSelectedVehicle(null)} 
      />
    </div>
  );
};

export default VehicleInventoryApp;
