import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import api from '../api/axios';

export default function IndiaMap() {
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHeatmapData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/heatmap/');
        setCities(response.data.data || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching heatmap data:', err);
        setError('Failed to load heatmap data');
        setCities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchHeatmapData();
  }, []);

  // Determine color based on risk score
  const getColor = (riskScore) => {
    if (riskScore >= 70) return '#dc2626'; // Red
    if (riskScore >= 40) return '#f97316'; // Orange
    return '#16a34a'; // Green
  };

  // Determine marker size based on risk score
  const getRadius = (riskScore) => {
    return Math.max(5, Math.min(20, riskScore / 5));
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-gray-600">
          <div className="animate-spin mb-4">⟳</div>
          <p>Loading risk map...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-100">
        <div className="text-red-600 text-center">
          <p className="text-lg font-semibold mb-2">⚠️ Error</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full">
      <MapContainer
        center={[20.5937, 78.9629]}
        zoom={5}
        style={{ width: '100%', height: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />

        {cities.map((city) => (
          <CircleMarker
            key={city.city}
            center={[city.lat, city.lng]}
            radius={getRadius(city.risk_score)}
            fillColor={getColor(city.risk_score)}
            color={getColor(city.risk_score)}
            weight={2}
            opacity={0.8}
            fillOpacity={0.7}
          >
            <Popup>
              <div className="text-sm">
                <p className="font-bold text-gray-800">{city.city}</p>
                <p className="text-gray-600">{city.state}</p>
                <div className="my-2 border-t border-gray-300 pt-2">
                  <p className="text-sm">
                    <span className="font-semibold">Risk Score:</span> {city.risk_score.toFixed(1)}
                  </p>
                  <p className="text-sm">
                    <span className="font-semibold">Confidence:</span> {(city.confidence * 100).toFixed(0)}%
                  </p>
                  {city.top_food && (
                    <p className="text-sm">
                      <span className="font-semibold">Top Risk:</span> {city.top_food}
                    </p>
                  )}
                  {city.top_adulterant && (
                    <p className="text-sm">
                      <span className="font-semibold">Adulterant:</span> {city.top_adulterant}
                    </p>
                  )}
                  <p className="text-sm">
                    <span className="font-semibold">Complaints:</span> {city.complaint_count}
                  </p>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
