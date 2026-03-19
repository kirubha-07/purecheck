import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function ShapChart({ city = 'Trichy', food = 'Milk', shapValues = [] }) {
  // Transform SHAP values for visualization
  const chartData = (shapValues || [])
    .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
    .slice(0, 10)
    .map((item) => ({
      feature: item.feature.length > 15 ? item.feature.substring(0, 12) + '...' : item.feature,
      'Risk Impact': item.value > 0 ? item.value : 0,
      'Safety Impact': item.value < 0 ? Math.abs(item.value) : 0,
    }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-1">
          🔍 Why This Risk Score?
        </h3>
        <p className="text-sm text-gray-600">
          AI explanation for {food} adulteration risk in {city}
        </p>
      </div>

      {chartData.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-gray-500">
          <p>No SHAP values available for visualization</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 250, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis type="category" dataKey="feature" width={240} tick={{ fontSize: 12 }} />
            <Tooltip 
              formatter={(value) => value.toFixed(3)}
              labelFormatter={(label) => `Feature: ${label}`}
            />
            <Legend />
            <Bar dataKey="Risk Impact" fill="#dc2626" />
            <Bar dataKey="Safety Impact" fill="#16a34a" />
          </BarChart>
        </ResponsiveContainer>
      )}

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-red-50 border border-red-200 rounded p-3">
          <p className="text-xs font-semibold text-red-900 mb-1">⬆️ Risk Factors</p>
          <p className="text-xs text-red-700">Features that increase adulteration risk</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded p-3">
          <p className="text-xs font-semibold text-green-900 mb-1">⬇️ Safety Factors</p>
          <p className="text-xs text-green-700">Features that decrease adulteration risk</p>
        </div>
      </div>
    </div>
  );
}
