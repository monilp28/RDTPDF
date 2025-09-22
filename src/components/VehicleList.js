import React, { useState, useEffect, useMemo } from 'react';
import '../App.css';

const VehicleList = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
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
  const [sortBy, setSortBy] = useState('year-desc');

  // Load vehicles from your scraper
  useEffect(() => {
    const loadVehicles = async () => {
      try {
        setLoading(true);
        // Use your existing scraper endpoint
        const response = await fetch('/api/scrape');
        const data = await response.json();
        
        if (data.ok && data.vehicles) {
          setVehicles(data.vehicles);
        } else {
          throw new Error(data.error || 'Failed to load vehicles');
        }
      } catch (err) {
        setError(err.message);
        console.error('Error loading vehicles:', err);
      } finally {
        setLoading(false);
      }
    };

    loadVehicles();
  }, []);

  // Get unique values for filters
  const uniqueMakes = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.make))].sort() : [];
  const uniqueYears = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.year))].sort((a, b) => b - a) : [];
  const uniqueFuelTypes = vehicles.length > 0 ? [...new Set(vehicles.map(v => v.fuel_type || 'Gasoline'))].sort() : [];

  // Filter and sort vehicles
  const filteredAndSortedVehicles = useMemo(() => {
    if (!vehicles || vehicles.length === 0) return [];
    
    let filtered = vehicles.filter(vehicle => {
      const searchableText = `${vehicle.year} ${vehicle.make} ${vehicle.model} ${vehicle.trim || ''} ${vehicle.stock_number || ''}`.toLowerCase();
      const matchesSearch = searchTerm === '' || searchableText.includes(searchTerm.toLowerCase());

      const matchesMake = filters.make === '' || vehicle.make === filters.make;
      const matchesYear = filters.year === '' || vehicle.year.toString() === filters.year;
      const matchesFuelType = filters.fuelType === '' || (vehicle.fuel_type || 'Gasoline') === filters.fuelType;
      
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

    // Sort vehicles
    filtered.sort((a, b) => {
      switch(sortBy) {
        case 'year-desc': return b.year - a.year;
        case 'year-asc': return a.year - b.year;
        case 'price-desc': return (parseFloat(b.price) || 0) - (parseFloat(a.price) || 0);
        case 'price-asc': return (parseFloat(a.price) || 0) - (parseFloat(b.price) || 0);
        case 'make-asc': return a.make.localeCompare(b.make);
        case 'mileage-asc': return (parseFloat(a.mileage) || 0) - (parseFloat(b.mileage) || 0);
        default: return 0;
      }
    });

    return filtered;
  }, [vehicles, searchTerm, filters, sortBy]);

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
    const posterHTML = `
      <div class="poster">
        <div class="poster-logo-center">
          <div class="brand-logo-lg" style="font-size: 28px; font-weight: 800; color: #1f2937; text-align: center;">
            RED DEER TOYOTA
          </div>
        </div>
        
        <div class="poster-model-center">${vehicle.year}</div>
        
        <div class="poster-info-box">
          <div class="info-line">
            <span class="info-label">${vehicle.make}</span>
            <span class="info-value">${vehicle.model}</span>
          </div>
          ${vehicle.trim ? `<div class="info-line"><span class="info-value">${vehicle.trim}</span></div>` : ''}
        </div>
        
        <div class="price-block">
          ${vehicle.sale_value && parseFloat(vehicle.sale_value) < parseFloat(vehicle.price) ? `
            <div class="price-sale-wrap">
              <div class="price-old">${formatPrice(vehicle.price)}</div>
              <div class="price-new-label">SALE PRICE</div>
              <div class="price-now">${formatPrice(vehicle.sale_value)}</div>
            </div>
          ` : `
            <div class="price-label-line">PRICE</div>
            <div class="price-main">${formatPrice(vehicle.price)}</div>
          `}
        </div>
        
        <div class="poster-specs-wide">
          <div class="spec">
            <label>Mileage</label>
            <span>${vehicle.mileage ? parseInt(vehicle.mileage).toLocaleString() + ' km' : 'N/A'}</span>
          </div>
          <div class="spec">
            <label>Engine</label>
            <span>${vehicle.engine || 'N/A'}</span>
          </div>
          <div class="spec">
            <label>Stock</label>
            <span>${vehicle.stock_number || 'N/A'}</span>
          </div>
        </div>
        
        <div class="poster-footer">
          Red Deer Toyota • ${vehicle.exterior_color || ''} • Stock #${vehicle.stock_number || 'N/A'}
        </div>
      </div>
    `;

    const newWindow = window.open('', '_blank', 'width=900,height=1200');
    newWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>Vehicle Poster - ${vehicle.year} ${vehicle.make} ${vehicle.model}</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap" rel="stylesheet">
        <style>
          ${document.querySelector('style') ? document.querySelector('style').textContent : ''}
          body { 
            margin: 20px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
          }
          @media print {
            body { margin: 0; }
            .poster { margin: 0; border: none; }
          }
        </style>
      </head>
      <body>
        ${posterHTML}
        <script>
          window.onload = function() {
            setTimeout(() => window.print(), 500);
          };
        </script>
      </body>
      </html>
    `);
    newWindow.document.close();
  };

  const VehicleCard = ({ vehicle }) => {
    const hasDiscount = vehicle.sale_value && parseFloat(vehicle.sale_value) < parseFloat(vehicle.price);
    const displayPrice = hasDiscount ? vehicle.sale_value : vehicle.price;
    const originalPrice = hasDiscount ? vehicle.price : null;

    return (
      <div className="card" style={{ 
        background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        border: '2px solid #e2e8f0',
        borderRadius: '16px',
        overflow: 'hidden',
        transition: 'all 0.3s ease',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.12)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
      }}>
        
        {/* Vehicle Image Section */}
        <div style={{ 
          position: 'relative', 
          height: '200px', 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '18px',
          fontWeight: '600'
        }}>
          {vehicle.image_urls && vehicle.image_urls[0] ? (
            <img 
              src={vehicle.image_urls[0]} 
              alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
              style={{ 
                width: '100%', 
                height: '100%', 
                objectFit: 'cover' 
              }}
              onError={(e) => {
                e.target.parentElement.innerHTML = `<span>${vehicle.make} ${vehicle.model}</span>`;
              }}
            />
          ) : (
            <span>{vehicle.make} {vehicle.model}</span>
          )}
          
          {/* Stock Number Badge */}
          <div style={{
            position: 'absolute',
            top: '12px',
            right: '12px',
            background: 'rgba(0,0,0,0.7)',
            color: 'white',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '12px',
            fontWeight: '600'
          }}>
            #{vehicle.stock_number}
          </div>

          {/* Sale Badge */}
          {hasDiscount && (
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              background: '#ef4444',
              color: 'white',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '700'
            }}>
              SALE
            </div>
          )}
        </div>

        {/* Vehicle Info */}
        <div style={{ padding: '20px' }}>
          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ 
              fontSize: '24px', 
              fontWeight: '800', 
              color: '#1e293b',
              margin: '0 0 4px 0'
            }}>
              {vehicle.year} {vehicle.make}
            </h3>
            <p style={{ 
              fontSize: '18px', 
              fontWeight: '600', 
              color: '#475569',
              margin: '0 0 4px 0'
            }}>
              {vehicle.model} {vehicle.trim || ''}
            </p>
            <p style={{ 
              fontSize: '14px', 
              color: '#64748b',
              margin: '0'
            }}>
              {vehicle.exterior_color} • {vehicle.body_style || 'Vehicle'}
            </p>
          </div>

          {/* Vehicle Stats */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: '1fr 1fr', 
            gap: '12px', 
            marginBottom: '16px' 
          }}>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              color: '#64748b'
            }}>
              <span style={{ fontSize: '16px' }}>📊</span>
              <span style={{ fontSize: '14px' }}>
                {vehicle.mileage ? parseInt(vehicle.mileage).toLocaleString() + ' km' : 'N/A'}
              </span>
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              color: '#64748b'
            }}>
              <span style={{ fontSize: '16px' }}>🚗</span>
              <span style={{ fontSize: '14px' }}>
                {vehicle.engine || vehicle.drivetrain || 'N/A'}
              </span>
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              color: '#64748b'
            }}>
              <span style={{ fontSize: '16px' }}>⛽</span>
              <span style={{ fontSize: '14px' }}>
                {vehicle.fuel_type || 'Gasoline'}
              </span>
            </div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '8px',
              color: '#64748b'
            }}>
              <span style={{ fontSize: '16px' }}>📅</span>
              <span style={{ fontSize: '14px' }}>
                {vehicle.transmission || 'Auto'}
              </span>
            </div>
          </div>

          {/* Pricing */}
          <div style={{ marginBottom: '20px' }}>
            {originalPrice && (
              <p style={{ 
                fontSize: '16px', 
                color: '#64748b', 
                textDecoration: 'line-through',
                margin: '0 0 4px 0',
                fontWeight: '500'
              }}>
                {formatPrice(originalPrice)}
              </p>
            )}
            <p style={{ 
              fontSize: '28px', 
              fontWeight: '900',
              color: hasDiscount ? '#dc2626' : '#1e293b',
              margin: '0'
            }}>
              {formatPrice(displayPrice)}
            </p>
            {hasDiscount && (
              <p style={{
                fontSize: '14px',
                color: '#059669',
                fontWeight: '600',
                margin: '4px 0 0 0'
              }}>
                Save {formatPrice(originalPrice - displayPrice)}!
              </p>
            )}
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <button 
              onClick={() => setSelectedVehicle(vehicle)}
              className="btn"
              style={{ 
                flex: '1',
                background: '#1e293b',
                color: 'white',
                border: 'none',
                padding: '12px 16px',
                borderRadius: '12px',
                fontWeight: '600',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.background = '#334155'}
              onMouseLeave={(e) => e.target.style.background = '#1e293b'}
            >
              👁️ View Details
            </button>
            <button 
              onClick={() => generatePoster(vehicle)}
              className="btn"
              style={{ 
                background: '#2563eb',
                color: 'white',
                border: 'none',
                padding: '12px 16px',
                borderRadius: '12px',
                fontWeight: '600',
                fontSize: '14px',
                cursor: 'pointer',
                minWidth: '50px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => e.target.style.background = '#1d4ed8'}
              onMouseLeave={(e) => e.target.style.background = '#2563eb'}
              title="Generate Poster"
            >
              📄
            </button>
          </div>
        </div>
      </div>
    );
  };

  const VehicleModal = ({ vehicle, onClose }) => {
    if (!vehicle) return null;
    
    const hasDiscount = vehicle.sale_value && parseFloat(vehicle.sale_value) < parseFloat(vehicle.price);
    const displayPrice = hasDiscount ? vehicle.sale_value : vehicle.price;
    const originalPrice = hasDiscount ? vehicle.price : null;
    
    return (
      <div style={{
        position: 'fixed',
        inset: '0',
        backgroundColor: 'rgba(0,0,0,0.5)',
        backdropFilter: 'blur(4px)',
        zIndex: '50',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '16px'
      }} onClick={onClose}>
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          maxWidth: '900px',
          width: '100%',
          maxHeight: '90vh',
          overflowY: 'auto',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
        }} onClick={(e) => e.stopPropagation()}>
          
          {/* Header Image */}
          <div style={{ position: 'relative', height: '300px' }}>
            {vehicle.image_urls && vehicle.image_urls[0] ? (
              <img 
                src={vehicle.image_urls[0]}
                alt={`${vehicle.year} ${vehicle.make} ${vehicle.model}`}
                style={{ 
                  width: '100%', 
                  height: '100%', 
                  objectFit: 'cover',
                  borderRadius: '16px 16px 0 0'
                }}
              />
            ) : (
              <div style={{
                width: '100%',
                height: '100%',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '24px',
                fontWeight: '600',
                borderRadius: '16px 16px 0 0'
              }}>
                {vehicle.make} {vehicle.model}
              </div>
            )}
            
            {/* Close Button */}
            <button 
              onClick={onClose}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'rgba(0,0,0,0.7)',
                color: 'white',
                border: 'none',
                padding: '8px',
                borderRadius: '50%',
                cursor: 'pointer',
                fontSize: '16px',
                width: '40px',
                height: '40px'
              }}
            >
              ✕
            </button>

            {/* Sale Badge */}
            {hasDiscount && (
              <div style={{
                position: 'absolute',
                top: '16px',
                left: '16px',
                background: '#ef4444',
                color: 'white',
                padding: '8px 16px',
                borderRadius: '20px',
                fontSize: '14px',
                fontWeight: '700'
              }}>
                ON SALE
              </div>
            )}
          </div>
          
          {/* Content */}
          <div style={{ padding: '32px' }}>
            {/* Title Section */}
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{ 
                fontSize: '36px', 
                fontWeight: '800', 
                color: '#1e293b',
                margin: '0 0 8px 0'
              }}>
                {vehicle.year} {vehicle.make} {vehicle.model}
              </h2>
              <p style={{ 
                fontSize: '20px', 
                color: '#64748b',
                margin: '0 0 4px 0'
              }}>
                {vehicle.trim || ''}
              </p>
              <p style={{ 
                fontSize: '16px', 
                color: '#94a3b8',
                margin: '0'
              }}>
                Stock #{vehicle.stock_number} • {vehicle.exterior_color}
              </p>
            </div>

            {/* Details Grid */}
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
              gap: '32px',
              marginBottom: '32px' 
            }}>
              {/* Vehicle Details */}
              <div>
                <h3 style={{ 
                  fontSize: '20px', 
                  fontWeight: '700', 
                  marginBottom: '16px',
                  color: '#1e293b'
                }}>
                  Vehicle Details
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {[
                    ['Body Style', vehicle.body_style || 'N/A'],
                    ['Mileage', vehicle.mileage ? parseInt(vehicle.mileage).toLocaleString() + ' km' : 'N/A'],
                    ['Engine', vehicle.engine || 'N/A'],
                    ['Transmission', vehicle.transmission || 'N/A'],
                    ['Drivetrain', vehicle.drivetrain || 'N/A'],
                    ['Fuel Type', vehicle.fuel_type || 'Gasoline'],
                    ['Exterior Color', vehicle.exterior_color || 'N/A'],
                    ['Interior Color', vehicle.interior_color || 'N/A']
                  ].map(([label, value]) => (
                    <div key={label} style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      paddingBottom: '8px',
                      borderBottom: '1px solid #e2e8f0'
                    }}>
                      <span style={{ color: '#64748b' }}>{label}:</span>
                      <span style={{ fontWeight: '600', color: '#1e293b' }}>{value}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Pricing */}
              <div>
                <h3 style={{ 
                  fontSize: '20px', 
                  fontWeight: '700', 
                  marginBottom: '16px',
                  color: '#1e293b'
                }}>
                  Pricing
                </h3>
                <div style={{ 
                  background: '#f8fafc', 
                  padding: '24px', 
                  borderRadius: '12px',
                  border: '2px solid #e2e8f0'
                }}>
                  {originalPrice && (
                    <p style={{ 
                      fontSize: '20px', 
                      color: '#64748b', 
                      textDecoration: 'line-through',
                      margin: '0 0 8px 0',
                      fontWeight: '500'
                    }}>
                      {formatPrice(originalPrice)}
                    </p>
                  )}
                  <p style={{ 
                    fontSize: '36px', 
                    fontWeight: '900',
                    color: hasDiscount ? '#dc2626' : '#1e293b',
                    margin: '0'
                  }}>
                    {formatPrice(displayPrice)}
                  </p>
                  {hasDiscount && (
                    <p style={{
                      fontSize: '16px',
                      color: '#059669',
                      fontWeight: '600',
                      margin: '8px 0 0 0'
                    }}>
                      Save {formatPrice(originalPrice - displayPrice)}!
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '16px' }}>
              <button 
                onClick={() => generatePoster(vehicle)}
                style={{
                  flex: '1',
                  background: '#2563eb',
                  color: 'white',
                  border: 'none',
                  padding: '16px 24px',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#1d4ed8'}
                onMouseLeave={(e) => e.target.style.background = '#2563eb'}
              >
                📄 Generate Poster
              </button>
              <button 
                onClick={onClose}
                style={{
                  padding: '16px 24px',
                  border: '2px solid #d1d5db',
                  color: '#374151',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  background: 'white',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => e.target.style.background = '#f9fafb'}
                onMouseLeave={(e) => e.target.style.background = 'white'}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="container">
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '16px',
          color: 'white'
        }}>
          <div style={{ 
            width: '50px', 
            height: '50px', 
            border: '4px solid rgba(255,255,255,0.3)', 
            borderTop: '4px solid white',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px auto'
          }}></div>
          <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>Loading Inventory</h2>
          <p style={{ opacity: '0.9' }}>Fetching the latest vehicle data...</p>
        </div>
        <style>
          {`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}
        </style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div style={{ 
          textAlign: 'center', 
          padding: '60px 20px',
          background: '#fee2e2',
          borderRadius: '16px',
          color: '#991b1b',
          border: '2px solid #fecaca'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
          <h2 style={{ fontSize: '24px', marginBottom: '8px' }}>Error Loading Inventory</h2>
          <p>{error}</p>
          <button 
            onClick={() => window.location.reload()}
            style={{
              marginTop: '16px',
              padding: '12px 24px',
              background: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)' 
    }}>
      {/* Enhanced Header */}
      <div style={{ 
        background: 'linear-gradient(135deg, #1e293b 0%, #334155 100%)', 
        color: 'white',
        boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
      }}>
        <div className="container" style={{ padding: '32px 16px' }}>
          <div style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '24px',
            alignItems: 'center' 
          }}>
            
            {/* Title Section */}
            <div style={{ textAlign: 'center' }}>
              <h1 style={{ 
                fontSize: '42px', 
                fontWeight: '900', 
                margin: '0 0 8px 0',
                background: 'linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                🚗 Red Deer Toyota Inventory
              </h1>
              <p style={{ 
                fontSize: '18px', 
                opacity: '0.9',
                margin: '0'
              }}>
                Find your perfect vehicle and generate professional posters
              </p>
            </div>
            
            {/* Search and Controls */}
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              gap: '16px',
              width: '100%',
              maxWidth: '800px'
            }}>
              
              {/* Search Bar */}
              <div style={{ position: 'relative' }}>
                <input
                  type="text"
                  placeholder="Search by make, model, year, or stock number..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '16px 16px 16px 50px',
                    fontSize: '16px',
                    border: '2px solid rgba(255,255,255,0.2)',
                    borderRadius: '12px',
                    background: 'rgba(255,255,255,0.1)',
                    color: 'white',
                    backdropFilter: 'blur(10px)',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => {
                    e.target.style.borderColor = 'rgba(255,255,255,0.4)';
                    e.target.style.background = 'rgba(255,255,255,0.15)';
                  }}
                  onBlur={(e) => {
                    e.target.style.borderColor = 'rgba(255,255,255,0.2)';
                    e.target.style.background = 'rgba(255,255,255,0.1)';
                  }}
                />
                <span style={{
                  position: 'absolute',
                  left: '18px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  fontSize: '18px',
                  opacity: '0.7'
                }}>
                  🔍
                </span>
              </div>

              {/* Controls Row */}
              <div style={{ 
                display: 'flex', 
                gap: '12px', 
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap'
              }}>
                
                {/* Sort Dropdown */}
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  style={{
                    padding: '12px 16px',
                    borderRadius: '8px',
                    border: '2px solid rgba(255,255,255,0.2)',
                    background: 'rgba(255,255,255,0.1)',
                    color: 'white',
                    fontSize: '14px',
                    backdropFilter: 'blur(10px)',
                    cursor: 'pointer'
                  }}
                >
                  <option value="year-desc" style={{color: '#333'}}>Newest First</option>
                  <option value="year-asc" style={{color: '#333'}}>Oldest First</option>
                  <option value="price-asc" style={{color: '#333'}}>Price: Low to High</option>
                  <option value="price-desc" style={{color: '#333'}}>Price: High to Low</option>
                  <option value="make-asc" style={{color: '#333'}}>Make: A to Z</option>
                  <option value="mileage-asc" style={{color: '#333'}}>Lowest Mileage</option>
                </select>

                {/* Filter Toggle */}
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '12px 20px',
                    background: showFilters ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)',
                    color: 'white',
                    border: '2px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: '600',
                    backdropFilter: 'blur(10px)',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
                  onMouseLeave={(e) => e.target.style.background = showFilters ? 'rgba(255,255,255,0.2)' : 'rgba(255,255,255,0.1)'}
                >
                  🔧 Filters
                </button>

                {/* Results Count */}
                <div style={{ 
                  fontSize: '14px', 
                  opacity: '0.9',
                  fontWeight: '600'
                }}>
                  {filteredAndSortedVehicles.length} of {vehicles.length} vehicles
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div style={{
          background: 'white',
          borderBottom: '1px solid #e2e8f0',
          boxShadow: '0 4px 6px rgba(0,0,0,0.05)'
        }}>
          <div className="container" style={{ padding: '24px 16px' }}>
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
              gap: '16px',
              marginBottom: '16px'
            }}>
              
              <select
                value={filters.make}
                onChange={(e) => setFilters({...filters, make: e.target.value})}
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  background: 'white'
                }}
              >
                <option value="">All Makes</option>
                {uniqueMakes.map(make => (
                  <option key={make} value={make}>{make}</option>
                ))}
              </select>

              <select
                value={filters.year}
                onChange={(e) => setFilters({...filters, year: e.target.value})}
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  background: 'white'
                }}
              >
                <option value="">All Years</option>
                {uniqueYears.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>

              <select
                value={filters.priceRange}
                onChange={(e) => setFilters({...filters, priceRange: e.target.value})}
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  background: 'white'
                }}
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
                style={{
                  padding: '12px 16px',
                  border: '2px solid #e2e8f0',
                  borderRadius: '8px',
                  fontSize: '14px',
                  background: 'white'
                }}
              >
                <option value="">All Fuel Types</option>
                {uniqueFuelTypes.map(fuel => (
                  <option key={fuel} value={fuel}>{fuel}</option>
                ))}
              </select>
            </div>

            <button
              onClick={clearFilters}
              style={{
                padding: '8px 16px',
                color: '#64748b',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600'
              }}
              onMouseEnter={(e) => e.target.style.color = '#1e293b'}
              onMouseLeave={(e) => e.target.style.color = '#64748b'}
            >
              Clear all filters
            </button>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="container" style={{ padding: '32px 16px' }}>
        {filteredAndSortedVehicles.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: '60px 20px',
            background: 'white',
            borderRadius: '16px',
            border: '2px solid #e2e8f0'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <h3 style={{ 
              fontSize: '24px', 
              fontWeight: '700', 
              color: '#64748b',
              marginBottom: '8px'
            }}>
              No vehicles found
            </h3>
            <p style={{ color: '#94a3b8', marginBottom: '20px' }}>
              Try adjusting your search terms or filters
            </p>
            <button
              onClick={clearFilters}
              style={{
                padding: '12px 24px',
                background: '#2563eb',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600'
              }}
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <div className="grid">
            {filteredAndSortedVehicles.map((vehicle, index) => (
              <VehicleCard 
                key={vehicle.stock_number || vehicle.id || index} 
                vehicle={vehicle} 
              />
            ))}
          </div>
        )}
      </div>

      {/* Vehicle Modal */}
      <VehicleModal 
        vehicle={selectedVehicle} 
        onClose={() => setSelectedVehicle(null)} 
      />

      {/* Custom Styles */}
      <style>
        {`
          input::placeholder {
            color: rgba(255, 255, 255, 0.7);
          }
          
          input:focus::placeholder {
            color: rgba(255, 255, 255, 0.5);
          }
          
          select option {
            background: white;
            color: #333;
          }
          
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 24px;
          }
          
          @media (max-width: 768px) {
            .grid {
              grid-template-columns: 1fr;
            }
          }
        `}
      </style>
    </div>
  );
};

export default VehicleList;
