import { useEffect, useState } from 'react';

// easeOutQuart easing function
const easeOutQuart = (t) => 1 - Math.pow(1 - t, 4);

export default function StatCard({ label, value, unit, change, changePositive }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const target = parseInt(value) || 0;
    const duration = 1200; // 1200ms
    const startTime = performance.now();

    const animate = (currentTime) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeOutQuart(progress);
      const current = Math.floor(target * eased);

      setDisplayValue(current);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [value]);

  return (
    <div
      style={{
        padding: '20px 24px',
        background: 'var(--bg-2)',
        borderRight: '1px solid var(--line)',
      }}
    >
      <div style={{ marginBottom: '12px' }}>
        <span className="label">{label}</span>
      </div>

      <div style={{ marginBottom: '8px', display: 'flex', alignItems: 'baseline', gap: '4px' }}>
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '36px',
            letterSpacing: '1px',
            color: 'var(--text)',
          }}
        >
          {displayValue}
        </span>
        {unit && (
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--red)',
            }}
          >
            {unit}
          </span>
        )}
      </div>

      {change !== undefined && (
        <div>
          <span
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              letterSpacing: '1px',
              color: changePositive ? 'var(--teal)' : 'var(--red)',
            }}
          >
            {changePositive ? '↑' : '↓'}{change}
          </span>
        </div>
      )}
    </div>
  );
}
