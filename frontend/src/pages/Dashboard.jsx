import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import api from '../api/axios';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalComplaints: 0,
    highRiskCities: 0,
    avgRiskScore: 0,
    lastUpdate: new Date(),
  });
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await api.get('/heatmap/');
        const cityData = response.data.data || [];

        if (cityData.length > 0) {
          const avgScore = (cityData.reduce((sum, city) => sum + city.risk_score, 0) / cityData.length).toFixed(1);
          const highRisk = cityData.filter(city => city.risk_score >= 70).length;
          const totalComplaints = cityData.reduce((sum, city) => sum + (city.complaint_count || 0), 0);

          setStats({
            totalComplaints,
            highRiskCities: highRisk,
            avgRiskScore: avgScore,
            lastUpdate: new Date(),
          });

          // Create mock chart data
          setChartData(
            cityData.slice(0, 10).map(city => ({
              city: city.city.substring(0, 8),
              risk: city.risk_score,
              complaints: city.complaint_count || 0,
            }))
          );
        }
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const StatCard = ({ icon, title, value, subtitle, color }) => (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${color}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">📊 Analytics Dashboard</h1>
          <p className="text-gray-600">Real-time food safety metrics across India</p>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <div className="animate-spin text-4xl mb-4">⟳</div>
            <p className="text-gray-600">Loading analytics...</p>
          </div>
        )}

        {/* Stats Grid */}
        {!loading && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <StatCard
                icon="🚨"
                title="High Risk Cities"
                value={stats.highRiskCities}
                subtitle="Risk score ≥ 70"
                color="border-red-500"
              />
              <StatCard
                icon="⚠️"
                title="Total Complaints"
                value={stats.totalComplaints}
                subtitle="Last 30 days"
                color="border-orange-500"
              />
              <StatCard
                icon="📈"
                title="Average Risk Score"
                value={stats.avgRiskScore}
                subtitle="Across all cities"
                color="border-yellow-500"
              />
              <StatCard
                icon="🔄"
                title="Last Update"
                value={stats.lastUpdate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                subtitle="Just now"
                color="border-blue-500"
              />
            </div>

            {/* Chart Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Risk Trend */}
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4">📈 Top Cities by Risk</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#dc2626" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#dc2626" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="city" />
                    <YAxis />
                    <Tooltip />
                    <Area type="monotone" dataKey="risk" stroke="#dc2626" fillOpacity={1} fill="url(#colorRisk)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* Complaint Distribution */}
              <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Complaints by City</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="city" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="complaints" stroke="#3b82f6" strokeWidth={2} dot={{ fill: '#3b82f6' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Info Box */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="font-bold text-blue-900 mb-2">💡 Key Insights</h3>
              <ul className="text-sm text-blue-900 space-y-1">
                <li>✓ {stats.highRiskCities} cities require immediate attention</li>
                <li>✓ Average risk score of {stats.avgRiskScore} indicates {stats.avgRiskScore > 50 ? 'high' : 'moderate'} adulteration threat</li>
                <li>✓ {stats.totalComplaints} citizen reports have been processed this month</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
