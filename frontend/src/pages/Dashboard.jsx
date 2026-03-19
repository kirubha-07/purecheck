import { useEffect, useState } from 'react';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getHeatmapData, getStats, exportToCSV } from '../api/axios';
import StatCard from '../components/StatCard';

export default function Dashboard() {
  const [stats, setStats] = useState({
    highRiskCities: 0,
    totalComplaints: 0,
    avgRiskScore: 0,
    lastPipeline: '2 hours ago',
  });
  const [chartData, setChartData] = useState([]);
  const [complaintData, setComplaintData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);

  useEffect(() => {
    const fetch = async () => {
      const { data: heatmapResponse } = await getHeatmapData();
      const { data: statsResponse } = await getStats();

      const heatmapData = heatmapResponse?.data || [];

      const highRiskCities = heatmapData.filter((c) => c.risk_score > 70).length;
      const avgRiskScore = heatmapData.length > 0
        ? Math.round(heatmapData.reduce((sum, c) => sum + (c.risk_score || 0), 0) / heatmapData.length)
        : 0;
      const totalComplaints = heatmapData.reduce((sum, c) => sum + (c.complaint_count || 0), 0);

      setStats({
        highRiskCities: statsResponse?.high_risk_cities ?? highRiskCities,
        totalComplaints: statsResponse?.total_complaints ?? totalComplaints,
        avgRiskScore: Math.round(statsResponse?.avg_risk_score ?? avgRiskScore),
        lastPipeline: '2 hours ago',
      });

      const cityChartData = [...heatmapData]
        .sort((a, b) => b.risk_score - a.risk_score)
        .slice(0, 10)
        .map((c) => ({
          name: c.city,
          value: Math.round(c.risk_score || 0),
        }));
      setChartData(cityChartData);

      const sourceData = [
        { name: 'FSSAI', value: statsResponse?.sources?.FSSAI || 0 },
        { name: 'NEWS', value: statsResponse?.sources?.NEWS || 0 },
        { name: 'CITIZEN', value: statsResponse?.sources?.CITIZEN || 0 },
      ];
      setComplaintData(sourceData);

      setLoading(false);
    };

    fetch();
  }, []);

  const handleExport = async () => {
    setExporting(true);
    setExportSuccess(false);
    const result = await exportToCSV();
    setExporting(false);
    if (result.success) {
      setExportSuccess(true);
      setTimeout(() => setExportSuccess(false), 3000);
    }
  };

  if (loading) {
    return (
      <div className="page layout" style={{ background: 'var(--bg)', padding: '32px 40px' }}>
        <div className="skeleton" style={{ height: '300px', marginBottom: '16px' }} />
        <div className="skeleton" style={{ height: '300px' }} />
      </div>
    );
  }

  return (
    <div className="page layout" style={{ background: 'var(--bg)', padding: '32px 40px' }}>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontFamily: 'var(--font-display)',
          fontSize: '24px',
          letterSpacing: '2px',
          color: 'var(--text)',
          borderBottom: '1px solid var(--line)',
          paddingBottom: '20px',
          marginBottom: '28px',
        }}
      >
        <div>SYSTEM ANALYTICS</div>
        <button
          onClick={handleExport}
          disabled={exporting}
          style={{
            background: 'transparent',
            border: '1px solid var(--line-2)',
            color: exportSuccess
              ? 'var(--teal)'
              : 'var(--text-3)',
            fontFamily: 'var(--font-mono)',
            fontSize: '9px',
            letterSpacing: '2px',
            textTransform: 'uppercase',
            padding: '8px 16px',
            cursor: exporting ? 'wait' : 'pointer',
            transition: 'all 200ms ease',
          }}
        >
          {exporting
            ? 'EXPORTING...'
            : exportSuccess
            ? '✓ EXPORTED'
            : 'EXPORT → POWER BI'}
        </button>
      </div>

      {/* STAT STRIP */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          border: '1px solid var(--line)',
          dividerColor: 'var(--line)',
        }}
      >
        <StatCard
          label="HIGH RISK CITIES"
          value={stats.highRiskCities}
          unit=""
          change="+2"
          changePositive={false}
        />
        <StatCard
          label="TOTAL COMPLAINTS"
          value={stats.totalComplaints}
          unit=""
          change="+14"
          changePositive={false}
        />
        <StatCard
          label="AVG RISK SCORE"
          value={stats.avgRiskScore}
          unit=""
          change="-1.2"
          changePositive={true}
        />
        <StatCard
          label="LAST PIPELINE"
          value={stats.lastPipeline === '2 hours ago' ? '2h' : '6h'}
          unit=""
        />
      </div>

      {/* CHARTS ROW */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: '3fr 2fr',
          gap: '1px',
          background: 'var(--line)',
          marginTop: '1px',
        }}
      >
        {/* Left — AreaChart */}
        <div
          style={{
            background: 'var(--bg-2)',
            padding: '24px',
          }}
        >
          <div className="label" style={{ marginBottom: '20px' }}>
            // city risk distribution
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="rgba(255, 45, 85, 0.3)" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="rgba(255, 45, 85, 0.3)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis
                dataKey="name"
                tick={{ fontFamily: 'var(--font-mono)', fontSize: 9, fill: 'var(--text-4)' }}
              />
              <YAxis
                tick={{ fontFamily: 'var(--font-mono)', fontSize: 9, fill: 'var(--text-4)' }}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-3)',
                  border: '1px solid var(--line-2)',
                  borderRadius: 0,
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10,
                }}
                labelStyle={{ color: 'var(--text)' }}
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke="var(--red)"
                fill="url(#riskGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Right — BarChart */}
        <div
          style={{
            background: 'var(--bg-2)',
            padding: '24px',
          }}
        >
          <div className="label" style={{ marginBottom: '20px' }}>
            // complaints by source
          </div>

          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={complaintData} layout="vertical">
              <CartesianGrid stroke="var(--line)" strokeDasharray="3 3" />
              <XAxis type="number" tick={{ fontFamily: 'var(--font-mono)', fontSize: 9, fill: 'var(--text-4)' }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontFamily: 'var(--font-mono)', fontSize: 9, fill: 'var(--text-4)' }}
                width={60}
              />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-3)',
                  border: '1px solid var(--line-2)',
                  borderRadius: 0,
                  fontFamily: 'var(--font-mono)',
                  fontSize: 10,
                }}
                labelStyle={{ color: 'var(--text)' }}
              />
              <Bar dataKey="value" fill="var(--red)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
