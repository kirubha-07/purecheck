import { useEffect, useRef, useState } from 'react';

export default function LiveFeed({ city, alerts = [] }) {
  const [displayAlerts, setDisplayAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(true);
  const feedRef = useRef(null);
  const seenIds = useRef(new Set());

  const formatTime = (timestamp) => {
    if (!timestamp) return 'just now';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    return `${Math.floor(diffHrs / 24)}d ago`;
  };

  const handleNewAlert = (alert) => {
    const alertId = alert?.id;
    if (alertId != null && seenIds.current.has(alertId)) return;
    if (alertId != null) seenIds.current.add(alertId);
    setDisplayAlerts((prev) => [alert, ...prev].slice(0, 20));
  };

  useEffect(() => {
    seenIds.current = new Set();
    setDisplayAlerts([]);

    (alerts || []).slice(0, 5).forEach((alert) => {
      handleNewAlert(alert);
    });
  }, [alerts, city]);

  useEffect(() => {
    if (!city) return;

    const ws = new WebSocket(`ws://localhost:8000/ws/alerts/${encodeURIComponent(city)}/`);

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const alert = JSON.parse(event.data);
        handleNewAlert(alert);
      } catch {
        // Ignore malformed websocket payloads.
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [city]);

  const getRiskColor = (riskScore) => {
    if (riskScore > 70) return 'var(--red)';
    if (riskScore >= 40) return 'var(--amber)';
    return 'var(--teal)';
  };

  return (
    <div
      style={{
        background: 'var(--bg-2)',
        borderLeft: '1px solid var(--line)',
        height: '100%',
        overflowY: 'auto',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--line)',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontFamily: 'var(--font-mono)',
          fontSize: '9px',
          color: 'var(--text-3)',
          letterSpacing: '2px',
          textTransform: 'uppercase',
        }}
      >
        <div
          style={{
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            background: 'var(--red)',
            animation: 'pulse 1.8s ease-in-out infinite',
            flexShrink: 0,
          }}
        />
        LIVE ALERT STREAM
      </div>

      {/* Connection status */}
      <div
        style={{
          padding: '8px 20px',
          fontFamily: 'var(--font-mono)',
          fontSize: '8px',
          letterSpacing: '1px',
          color: 'var(--text-4)',
        }}
      >
        {isConnected ? '● CONNECTED' : '◌ CONNECTING...'}
      </div>

      {/* Alerts list */}
      <div ref={feedRef}>
        {displayAlerts.length === 0 ? (
          <div
            style={{
              padding: '32px 20px',
              textAlign: 'center',
              fontFamily: 'var(--font-body)',
              fontSize: '12px',
              color: 'var(--text-3)',
            }}
          >
            No alerts yet for {city}
          </div>
        ) : (
          displayAlerts.map((alert, idx) => {
            const riskColor = getRiskColor(alert.risk_score || 0);
            return (
              <div
                key={`${alert.id || idx}`}
                style={{
                  display: 'flex',
                  gap: '14px',
                  padding: '12px 16px 12px 20px',
                  borderBottom: '1px solid var(--line)',
                  animation: `fadeUp ${300 + idx * 50}ms ease forwards`,
                  alignItems: 'flex-start',
                }}
              >
                {/* Left bar */}
                <div
                  style={{
                    width: '1px',
                    background: riskColor,
                    alignSelf: 'stretch',
                    minHeight: '50px',
                  }}
                />

                {/* Content */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  {/* Food + city */}
                  <div
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: 'var(--text)',
                      textTransform: 'capitalize',
                      marginBottom: '3px',
                    }}
                  >
                    {alert.food_item} in {alert.city}
                  </div>

                  {/* Message */}
                  <div
                    style={{
                      fontFamily: 'var(--font-body)',
                      fontSize: '11px',
                      fontWeight: 300,
                      color: 'var(--text-3)',
                      lineHeight: '1.6',
                      marginBottom: '4px',
                      overflow: 'hidden',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                    }}
                  >
                    {alert.message || 'Alert details'}
                  </div>

                  {/* Time */}
                  <div
                    style={{
                      fontFamily: 'var(--font-mono)',
                      fontSize: '9px',
                      color: 'var(--text-4)',
                      letterSpacing: '1px',
                      textTransform: 'uppercase',
                    }}
                  >
                    {formatTime(alert.created_at || alert.timestamp)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
