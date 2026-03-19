import { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getHeatmapData } from '../api/axios';

function MapHoverHandler() {
  const map = useMapEvents({});
  const markerRefs = useRef({});

  return null;
}

export default function IndiaMap({ height = '100%', zoom = 5 }) {
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      const { data, error } = await getHeatmapData();
      if (!error && data && data.data) {
        setCities(data.data || []);
      }
      setLoading(false);
    };
    fetch();
  }, []);

  const getRiskColor = (riskScore) => {
    if (riskScore > 70) return 'var(--red)';
    if (riskScore >= 40) return 'var(--amber)';
    return 'var(--teal)';
  };

  const getRadius = (riskScore) => {
    return Math.max(4, Math.min(14, riskScore / 9));
  };

  if (loading) {
    return (
      <div style={{ width: '100%', height: '100%', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="skeleton" style={{ width: '200px', height: '40px' }} />
      </div>
    );
  }

  const colors = {
    red: '#FF2D55',
    amber: '#FF8C00',
    teal: '#00C896',
  };

  const getColorHex = (riskScore) => {
    if (riskScore > 70) return colors.red;
    if (riskScore >= 40) return colors.amber;
    return colors.teal;
  };

  return (
    <MapContainer
      center={[20.5937, 78.9629]}
      zoom={zoom || 5}
      minZoom={4}
      maxZoom={8}
      style={{ width: '100%', height }}
    >
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        attribution="© CartoDB"
      />

      {cities.map((city, idx) => {
        const color = getColorHex(city.risk_score);
        const radius = getRadius(city.risk_score);

        return (
          <CircleMarker
            key={`${city.city}-${idx}`}
            center={[city.lat, city.lng]}
            radius={radius}
            fillColor={color}
            color={color}
            weight={0}
            opacity={0.85}
            fillOpacity={0.85}
            eventHandlers={{
              mouseover: (e) => {
                e.target.setStyle({ weight: 1 });
              },
              mouseout: (e) => {
                e.target.setStyle({ weight: 0 });
              },
            }}
          >
            <Popup>
              <div>
                <div
                  style={{
                    fontFamily: 'var(--font-display)',
                    fontSize: '16px',
                    color: 'var(--text)',
                    marginBottom: '6px',
                  }}
                >
                  {city.city}
                </div>

                <div style={{ fontSize: '9px', color: 'var(--text-3)', marginBottom: '8px' }}>
                  {city.state}
                </div>

                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '22px',
                    color: color,
                    marginBottom: '4px',
                  }}
                >
                  {city.risk_score.toFixed(0)}
                </div>

                <div style={{ fontSize: '9px', color: 'var(--text-3)', marginTop: '8px' }}>
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '9px',
                      letterSpacing: '1px',
                      textTransform: 'uppercase',
                      marginBottom: '3px',
                    }}
                  >
                    LAST UPDATED
                  </div>
                  {city.updated_at ? new Date(city.updated_at).toLocaleString() : '6 hours ago'}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        );
      })}
    </MapContainer>
  );
}
