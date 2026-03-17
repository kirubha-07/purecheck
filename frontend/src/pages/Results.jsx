import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { riskAPI } from '../api/axios';
import RiskCard from '../components/RiskCard';
import LiveFeed from '../components/LiveFeed';

export default function Results() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const city = searchParams.get('city');
  
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!city) {
      navigate('/');
      return;
    }

    const fetchRisks = async () => {
      try {
        setLoading(true);
        const data = await riskAPI.getTopRisks(city);
        setRisks(data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch risk data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRisks();
  }, [city, navigate]);

  if (!city) return null;

  const currentMonth = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/')}
            className="text-green-600 hover:text-green-700 font-semibold mb-4 flex items-center gap-1"
          >
            ← Back to Home
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Food Safety Alerts for {city}
          </h1>
          <p className="text-gray-600">
            Last updated: {currentMonth} • Top 5 High-Risk Items
          </p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin text-4xl mb-4">🔄</div>
            <p className="text-gray-600">Loading risk data...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* No Data State */}
        {!loading && !error && risks.length === 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center mb-8">
            <p className="text-blue-800 text-lg">
              No risk data available for {city} yet. Please try another city or check back later.
            </p>
          </div>
        )}

        {/* Risk Cards Grid */}
        {!loading && risks.length > 0 && (
          <>
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {risks.map((risk) => (
                <RiskCard
                  key={risk.id}
                  food_item={risk.food_item}
                  risk_score={risk.risk_score}
                  adulterant={risk.adulterant}
                  complaint_count={risk.complaint_count}
                  last_updated={risk.last_updated}
                />
              ))}
            </div>

            {/* Live Feed */}
            <div className="mb-8">
              <LiveFeed city={city} />
            </div>

            {/* Report Button */}
            <div className="text-center">
              <button
                onClick={() => navigate(`/report?city=${encodeURIComponent(city)}`)}
                className="px-8 py-3 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition"
              >
                📝 Report an Incident in {city}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
