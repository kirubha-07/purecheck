export default function ShapChart({ confidence, risk_score }) {
  // Mock SHAP features
  const features = [
    { name: 'Complaint Count', value: 0.35, impact: 'increases' },
    { name: 'Severity Average', value: 0.22, impact: 'increases' },
    { name: 'Adulterant Count', value: 0.18, impact: 'increases' },
    { name: 'Trend Score', value: -0.12, impact: 'decreases' },
    { name: 'Recency Weight', value: 0.08, impact: 'increases' },
  ];

  const maxValue = Math.max(...features.map(f => Math.abs(f.value)));

  return (
    <div
      style={{
        backgroundColor: 'var(--bg-tertiary)',
        border: '1px solid var(--border)',
        borderRadius: '0 0 8px 8px',
        padding: '20px',
        marginTop: '-1px',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
          paddingBottom: '12px',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '10px',
            fontWeight: 500,
            letterSpacing: '2px',
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
          }}
        >
          PREDICTION BREAKDOWN
        </span>
        <div
          style={{
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '4px',
            padding: '3px 8px',
            fontFamily: "'Inter', sans-serif",
            fontSize: '11px',
            color: 'var(--accent-blue)',
          }}
        >
          {Math.round(confidence * 100)}% confident
        </div>
      </div>

      {/* Feature bars */}
      <div style={{ marginBottom: '16px' }}>
        {features.map((feature, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '12px',
              animation: `fadeInUp ${300 + idx * 50}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
              opacity: 0,
            }}
          >
            <span
              style={{
                fontFamily: "'Inter', sans-serif",
                fontSize: '12px',
                color: 'var(--text-secondary)',
                width: '140px',
                flexShrink: 0,
              }}
            >
              {feature.name}
            </span>

            <div
              style={{
                flex: 1,
                height: '4px',
                backgroundColor: 'var(--border-bright)',
                borderRadius: '2px',
                overflow: 'hidden',
              }}
            >
              <div
                style={{
                  height: '100%',
                  backgroundColor:
                    feature.value > 0 ? 'var(--accent-red)' : 'var(--accent-green)',
                  width: `${(Math.abs(feature.value) / maxValue) * 100}%`,
                  animation: `riskBarFill 500ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards`,
                  borderRadius: '2px',
                }}
              />
            </div>

            <span
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '11px',
                color: feature.value > 0 ? 'var(--accent-red)' : 'var(--accent-green)',
                width: '60px',
                textAlign: 'right',
                flexShrink: 0,
              }}
            >
              {feature.value > 0 ? '+' : ''}{feature.value.toFixed(2)}
            </span>
          </div>
        ))}
      </div>

      {/* Explanation text */}
      <div
        style={{
          paddingTop: '12px',
          borderTop: '1px solid var(--border)',
        }}
      >
        <span
          style={{
            fontFamily: "'Inter', sans-serif",
            fontSize: '13px',
            color: 'var(--text-secondary)',
            lineHeight: '1.7',
            fontStyle: 'italic',
          }}
        >
          " This food item shows elevated risk primarily due to a high number of
          recent complaints and multiple reported adulterants. The model is confident
          in this prediction based on historical patterns.
        </span>
      </div>
    </div>
  );
}
