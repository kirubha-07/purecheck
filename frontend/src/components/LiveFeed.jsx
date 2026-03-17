import { useEffect, useRef, useState } from 'react';
import RiskBadge from './RiskBadge';

export default function LiveFeed({ city }) {
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const feedRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    if (!city) return;

    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/alerts/${city.toLowerCase()}/`;

    console.log(`[LiveFeed] Connecting to WebSocket: ${wsUrl}`);

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('[LiveFeed] WebSocket connected');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('[LiveFeed] Received alert:', message);
        
        // Add new alert to the top of the list
        setAlerts((prev) => [message, ...prev].slice(0, 20));
        
        // Auto-scroll to newest
        if (feedRef.current) {
          feedRef.current.scrollTop = 0;
        }
      } catch (error) {
        console.error('[LiveFeed] Error parsing message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('[LiveFeed] WebSocket error:', error);
      setIsConnected(false);
    };

    ws.onclose = () => {
      console.log('[LiveFeed] WebSocket closed');
      setIsConnected(false);
    };

    wsRef.current = ws;

    return () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [city]);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">🔴 Live Alert Feed</h2>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'} animate-pulse`} />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Connecting...'}
          </span>
        </div>
      </div>

      <div
        ref={feedRef}
        className="space-y-3 max-h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50"
      >
        {alerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p className="text-lg">📡 Waiting for alerts...</p>
            <p className="text-sm mt-2">New alerts will appear here in real-time</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={`${alert.id}-${index}`}
              className="border-l-4 border-orange-500 bg-white p-3 rounded hover:shadow-md transition"
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold text-gray-800">{alert.food_item}</span>
                <RiskBadge level={alert.risk_level} />
              </div>
              <p className="text-sm text-gray-700 mb-2">{alert.message}</p>
              <p className="text-xs text-gray-500">
                {new Date(alert.created_at).toLocaleString()}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
