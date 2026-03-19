export default function RiskBadge({ level }) {
  const levelMap = {
    CRITICAL: { color: 'var(--red)', background: 'var(--red-dim)', border: '1px solid var(--red-line)' },
    HIGH: { color: 'var(--red)', background: 'transparent', border: '1px solid rgba(255, 45, 85, 0.2)' },
    MEDIUM: { color: 'var(--amber)', background: 'transparent', border: '1px solid rgba(255, 140, 0, 0.2)' },
    LOW: { color: 'var(--teal)', background: 'transparent', border: '1px solid rgba(0, 200, 150, 0.2)' },
  };

  const levelStyle = levelMap[level] || levelMap.LOW;

  return (
    <span
      style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '8px',
        fontWeight: 500,
        letterSpacing: '2px',
        textTransform: 'uppercase',
        padding: '3px 7px',
        display: 'inline-block',
        borderRadius: 0,
        color: levelStyle.color,
        background: levelStyle.background,
        border: levelStyle.border,
      }}
    >
      {level}
    </span>
  );
}
