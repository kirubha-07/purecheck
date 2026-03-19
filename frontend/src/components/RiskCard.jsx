import { useState, useEffect } from 'react';
import RiskBadge from './RiskBadge';
import ShapChart from './ShapChart';
import { ChevronDown } from 'lucide-react';

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

export default function RiskCard({ food_item, risk_score, adulterant, complaint_count, last_updated, shap }) {
  const [showShap, setShowShap] = useState(false);
  const [animateBar, setAnimateBar] = useState(false);

  useEffect(() => {
    setAnimateBar(true);
  }, []);

  const getEmoji = (food) => {
    const key = food?.toLowerCase();
    for (const [keyword, emoji] of Object.entries(FOOD_EMOJIS)) {
      if (key?.includes(keyword)) return emoji;
    }
    return '🍽️';
  };

  const getRiskColor = (score) => {
    if (score > 70) return '#FF4757';
    if (score >= 40) return '#F0A500';
    return '#00D68F';
  };

  const confidence = Math.random() * 0.3 + 0.7; // Mock confidence 0.7-1.0

  return (
    <div className="card">
      {/* Top row: Food + Badge */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '28px' }}>{getEmoji(food_item)}</span>
          <span
            style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: '16px',
              fontWeight: 600,
              color: 'var(--text-primary)',
            }}
          >
            {food_item}
          </span>
        </div>
        <RiskBadge risk={risk_score} />
      </div>

      {/* Risk score row */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-end',
          marginBottom: '12px',
        }}
      >
        <span
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: '10px',
            fontWeight: 500,
            letterSpacing: '2px',
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
          }}
        >
          RISK SCORE
        </span>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '28px',
            fontWeight: 500,
            color: getRiskColor(risk_score),
          }}
        >
          {Math.round(risk_score)}
        </span>
      </div>

      {/* Risk bar */}
      <div
        style={{
          height: '3px',
          backgroundColor: 'var(--border-bright)',
          borderRadius: '2px',
          marginBottom: '12px',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            height: '100%',
            backgroundColor: getRiskColor(risk_score),
            width: animateBar ? `${risk_score}%` : '0%',
            animation: animateBar
              ? `riskBarFill 600ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards`
              : 'none',
            borderRadius: '2px',
          }}
        />
      </div>

      {/* Details row */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: '12px',
          paddingBottom: '12px',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div>
          <span
            style={{
              fontFamily: "'Inter', sans-serif",
              fontSize: '12px',
              color: 'var(--text-secondary)',
            }}
          >
            {adulterant || 'N/A'}
          </span>
        </div>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '12px',
            color: 'var(--text-muted)',
          }}
        >
          {complaint_count} reports
        </span>
      </div>

      {/* Confidence bar */}
      <div style={{ marginBottom: '16px' }}>
        <div
          style={{
            height: '2px',
            backgroundColor: 'var(--border-bright)',
            borderRadius: '1px',
            overflow: 'hidden',
            marginBottom: '6px',
          }}
        >
          <div
            style={{
              height: '100%',
              backgroundColor: 'var(--accent-blue)',
              width: `${confidence * 100}%`,
            }}
          />
        </div>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          {Math.round(confidence * 100)}% confident
        </span>
      </div>

      {/* Why button */}
      <button
        onClick={() => setShowShap(!showShap)}
        style={{
          width: '100%',
          fontFamily: "'Inter', sans-serif",
          fontSize: '12px',
          color: 'var(--accent-blue)',
          backgroundColor: 'transparent',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '4px',
          padding: '8px',
          cursor: 'pointer',
          transition: 'background-color 200ms cubic-bezier(0.4, 0, 0.2, 1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
        }}
        onMouseEnter={(e) => {
          e.target.style.backgroundColor = 'rgba(59, 130, 246, 0.08)';
        }}
        onMouseLeave={(e) => {
          e.target.style.backgroundColor = 'transparent';
        }}
      >
        Why this score?
        <ChevronDown
          size={14}
          style={{
            transform: showShap ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 200ms cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </button>

      {/* SHAP Chart */}
      {showShap && (
        <ShapChart confidence={confidence} risk_score={risk_score} />
      )}
    </div>
  );
}
