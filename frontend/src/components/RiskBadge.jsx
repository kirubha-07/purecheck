export default function RiskBadge({ level }) {
  const getStyles = (level) => {
    switch (level) {
      case 'HIGH':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getEmoji = (level) => {
    switch (level) {
      case 'HIGH': return '🚨';
      case 'MEDIUM': return '⚠️';
      case 'LOW': return '✅';
      default: return '❓';
    }
  };

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold border ${getStyles(level)}`}>
      {getEmoji(level)} {level}
    </span>
  );
}
