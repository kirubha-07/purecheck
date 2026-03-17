import RiskBadge from './RiskBadge';

const FOOD_EMOJIS = {
  'milk': '🥛',
  'rice': '🍚',
  'oil': '🫙',
  'sweets': '🍬',
  'vegetables': '🥦',
  'fruits': '🍎',
  'ghee': '🧈',
  'paneer': '🧀',
  'turmeric': '🟡',
  'chilli': '🌶️',
};

export default function RiskCard({ food_item, risk_score, adulterant, complaint_count, last_updated }) {
  const getRiskLevel = (score) => {
    if (score > 70) return 'HIGH';
    if (score > 40) return 'MEDIUM';
    return 'LOW';
  };

  const getRiskColor = (score) => {
    if (score > 70) return 'from-red-500 to-red-600';
    if (score > 40) return 'from-yellow-500 to-yellow-600';
    return 'from-green-500 to-green-600';
  };

  const getEmoji = (food) => {
    const key = food?.toLowerCase();
    for (const [keyword, emoji] of Object.entries(FOOD_EMOJIS)) {
      if (key?.includes(keyword)) return emoji;
    }
    return '🍽️';
  };

  const level = getRiskLevel(risk_score);
  const timeAgo = new Date(last_updated);
  const timeString = timeAgo.toLocaleDateString();

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 border-l-4 border-orange-500">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{getEmoji(food_item)}</span>
          <div>
            <h3 className="text-lg font-bold text-gray-800">{food_item.toUpperCase()}</h3>
            <p className="text-sm text-gray-600">Primary Adulterant: {adulterant}</p>
          </div>
        </div>
        <RiskBadge level={level} />
      </div>

      {/* Risk Score Bar */}
      <div className="mb-4">
        <div className="flex justify-between mb-1">
          <span className="text-sm font-semibold text-gray-700">Risk Score</span>
          <span className="text-sm font-bold text-gray-900">{risk_score.toFixed(1)}/100</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`bg-gradient-to-r ${getRiskColor(risk_score)} h-full rounded-full transition-all duration-500`}
            style={{ width: `${risk_score}%` }}
          />
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-gray-600">Complaints</p>
          <p className="text-lg font-bold text-blue-600">{complaint_count}</p>
        </div>
        <div className="bg-purple-50 p-3 rounded">
          <p className="text-gray-600">Last Updated</p>
          <p className="text-sm font-semibold text-purple-600">{timeString}</p>
        </div>
      </div>
    </div>
  );
}
