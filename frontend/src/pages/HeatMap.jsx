import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import IndiaMap from '../components/IndiaMap';
import { getHeatmapData } from '../api/axios';

export default function HeatMap() {
  const navigate = useNavigate();
  const [cities, setCities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      const { data } = await getHeatmapData();
      if (data && data.data) {
        const sorted = (data.data || []).sort((a, b) => b.risk_score - a.risk_score);
        setCities(sorted);
      }
      setLoading(false);
    };

    fetch();
  }, []);

  const getRiskColor = (score) => {
    if (score > 70) return { color: '#FF2D55', dim: 'rgba(255, 45, 85, 0.12)' };
    if (score >= 40) return { color: '#FF8C00', dim: 'rgba(255, 140, 0, 0.12)' };
    return { color: '#00C896', dim: 'rgba(0, 200, 150, 0.12)' };
  };

  return (
    <div className="page layout" style={{ background: 'var(--bg)' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', height: 'calc(100vh - 50px)', gap: 0 }}>
        {/* Left — Full-height Map */}
        <div style={{ overflow: 'hidden', background: 'var(--bg-2)', height: '100%' }}>
          <IndiaMap height="100%" zoom={5} />
        </div>

        {/* Right — Sidebar */}
        <div
          style={{
            padding: '28px 24px',
            background: 'var(--bg-2)',
            borderLeft: '1px solid var(--line)',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          {/* Top label */}
          <div className="label" style={{ marginBottom: '8px' }}>
            // city risk index
          </div>

          {/* Subtitle */}
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              color: 'var(--text-4)',
              letterSpacing: '1px',
              marginBottom: '20px',
            }}
          >
            30+ cities monitored · 6h cycle
          </div>

          {/* Divider */}
          <div style={{ height: '1px', background: 'var(--line)', marginBottom: '20px' }} />

          {/* City list */}
          <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', marginBottom: '20px' }}>
            {loading ? (
              <div className="skeleton" style={{ height: '300px' }} />
            ) : cities.length === 0 ? (
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '9px',
                  color: 'var(--text-4)',
                 padding: '20px 0',
                }}
              >
                No city data
              </div>
            ) : (
              cities.slice(0, 30).map((city, idx) => {
                const colors = getRiskColor(city.risk_score);

                return (
                  <div
                    key={`${city.city}-${idx}`}
                    style={{
                      padding: '10px 0',
                      borderBottom: '1px solid var(--line)',
                      display: 'grid',
                      gridTemplateColumns: '20px 8px 1fr auto auto',
                      gap: '8px',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: 'opacity 150ms',
                    }}
                    onClick={() => navigate(`/results?city=${encodeURIComponent(city.city)}`)}
                    onMouseEnter={(e) => (e.currentTarget.style.opacity = '0.7')}
                    onMouseLeave={(e) => (e.currentTarget.style.opacity = '1')}
                  >
                    {/* Rank */}
                    <div
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '9px',
                        color: 'var(--text-4)',
                      }}
                    >
                      {idx + 1}
                    </div>

                    {/* Dot */}
                    <div
                      style={{
                        width: '4px',
                        height: '4px',
                        borderRadius: '50%',
                        background: colors.color,
                        flexShrink: 0,
                      }}
                    />

                    {/* City name */}
                    <div
                      style={{
                        fontFamily: 'var(--font-body)',
                        fontSize: '12px',
                        color: 'var(--text-2)',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {city.city}
                    </div>

                    {/* Bar */}
                    <div
                      style={{
                        flex: 1,
                        height: '1px',
                        background: 'var(--line-2)',
                        position: 'relative',
                        minWidth: '30px',
                      }}
                    >
                      <div
                        style={{
                          position: 'absolute',
                          height: '100%',
                          background: colors.color,
                          width: `${Math.min(100, city.risk_score)}%`,
                        }}
                      />
                    </div>

                    {/* Score */}
                    <div
                      style={{
                        fontFamily: 'var(--font-mono)',
                        fontSize: '12px',
                        color: colors.color,
                        textAlign: 'right',
                        minWidth: '40px',
                      }}
                    >
                      {city.risk_score.toFixed(0)}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Legend */}
          <div style={{ paddingTop: '20px', borderTop: '1px solid var(--line)' }}>
            <div className="label" style={{ marginBottom: '12px' }}>
              // risk thresholds
            </div>

            {[
              { color: '#FF2D55', text: 'HIGH RISK    >70' },
              { color: '#FF8C00', text: 'MEDIUM RISK  40–70' },
              { color: '#00C896', text: 'LOW RISK     <40' },
            ].map((item, idx) => (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '9px',
                  color: 'var(--text-3)',
                  letterSpacing: '1px',
                  marginBottom: '6px',
                }}
              >
                <div
                  style={{
                    width: '4px',
                    height: '4px',
                    borderRadius: '50%',
                    background: item.color,
                    flexShrink: 0,
                  }}
                />
                {item.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
