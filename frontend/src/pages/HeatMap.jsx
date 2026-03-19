import { useState, useEffect } from 'react';
import IndiaMap from '../components/IndiaMap';
import api from '../api/axios';

export default function HeatMap() {
  const [topCities, setTopCities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopCities = async () => {
      try {
        const response = await api.get('/heatmap/');
        const sorted = (response.data.data || [])
          .sort((a, b) => b.risk_score - a.risk_score)
          .slice(0, 5);
        setTopCities(sorted);
      } catch (err) {
        console.error('Error fetching top cities:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchTopCities();
  }, []);

  const getRiskLevel = (score) => {
    if (score >= 70) return { label: 'CRITICAL', color: 'text-red-600', bg: 'bg-red-50' };
    if (score >= 40) return { label: 'HIGH', color: 'text-orange-600', bg: 'bg-orange-50' };
    return { label: 'MEDIUM', color: 'text-yellow-600', bg: 'bg-yellow-50' };
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🗺️ India Food Safety Risk Map
          </h1>
          <p className="text-gray-600">Real-time adulteration risk across major Indian cities</p>
        </div>

        {/* Main Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Map Container - 3 cols */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-gray-200" style={{ height: '600px' }}>
              <IndiaMap />
            </div>
          </div>

          {/* Sidebar - 1 col */}
          <div className="space-y-4">
            {/* Legend */}
            <div className="bg-white rounded-lg shadow-md p-4 border border-gray-200">
              <h3 className="font-bold text-gray-800 mb-3 flex items-center">
                <span className="mr-2">📊 Risk Scale</span>
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-red-600"></div>
                  <span className="text-sm text-gray-700">Critical (70+)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-orange-400"></div>
                  <span className="text-sm text-gray-700">High (40-70)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 rounded-full bg-green-600"></div>
                  <span className="text-sm text-gray-700">Medium (&lt;40)</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Marker size indicates relative risk intensity
              </p>
            </div>

            {/* Top 5 Risky Cities */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200">
              <div className="bg-gradient-to-r from-red-50 to-orange-50 px-4 py-3 border-b border-gray-200">
                <h3 className="font-bold text-gray-800">🚨 Riskiest Cities</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {loading ? (
                  <div className="p-4 text-center text-gray-500 text-sm">Loading...</div>
                ) : topCities.length === 0 ? (
                  <div className="p-4 text-center text-gray-500 text-sm">No data available</div>
                ) : (
                  topCities.map((city, idx) => {
                    const risk = getRiskLevel(city.risk_score);
                    return (
                      <div key={city.city} className={`p-3 ${risk.bg}`}>
                        <div className="flex items-start justify-between mb-1">
                          <div>
                            <p className="font-semibold text-gray-800 text-sm">
                              {idx + 1}. {city.city}
                            </p>
                            <p className="text-xs text-gray-600">{city.state}</p>
                          </div>
                          <span className={`text-xs font-bold ${risk.color}`}>
                            {risk.label}
                          </span>
                        </div>
                        <div className="text-xs text-gray-700 mt-2">
                          <p>Score: <span className="font-semibold">{city.risk_score.toFixed(1)}</span></p>
                          {city.top_food && (
                            <p className="truncate">Food: <span className="font-semibold">{city.top_food}</span></p>
                          )}
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-xs text-blue-900 leading-relaxed">
                <span className="font-semibold">💡 Tip:</span> Click on any marker to see detailed risk information for that city.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
