import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();
  const [city, setCity] = useState('');

  const handleSearch = () => {
    if (city.trim()) {
      navigate(`/results?city=${encodeURIComponent(city.trim())}`);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="page layout" style={{ background: 'var(--bg)' }}>
      {/* SECTION 1 — Hero */}
      <div style={{ padding: '64px 40px 0' }}>
        {/* Eyebrow */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '18px',
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            color: 'var(--red)',
            letterSpacing: '2px',
            textTransform: 'uppercase',
          }}
        >
          Food Safety Intelligence Platform
          <div style={{ width: '36px', height: '1px', background: 'rgba(255, 45, 85, 0.4)' }} />
        </div>

        {/* H1 with watermark */}
        <div style={{ position: 'relative', overflow: 'hidden', marginBottom: '20px' }}>
          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '80px',
              lineHeight: 0.92,
              letterSpacing: '3px',
              color: 'var(--text)',
              position: 'relative',
              zIndex: 1,
            }}
          >
            PREDICT.<br />
            <span style={{ color: 'var(--red)' }}>PROTECT.</span><br />
            PREVENT.
          </h1>

          {/* Watermark */}
          <div
            style={{
              position: 'absolute',
              right: '-30px',
              top: 0,
              fontFamily: 'var(--font-display)',
              fontSize: '180px',
              color: 'rgba(255, 255, 255, 0.012)',
              letterSpacing: '12px',
              zIndex: 0,
              pointerEvents: 'none',
            }}
          >
            PURECHECK
          </div>
        </div>

        {/* Subtext */}
        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '13px',
            fontWeight: 300,
            color: 'var(--text-2)',
            lineHeight: 1.9,
            maxWidth: '400px',
            marginBottom: '36px',
          }}
        >
          Real-time adulteration risk scoring for 30+ Indian cities. Powered by XGBoost ML, BERT NLP, and SHAP explainability. Updated every 6 hours from FSSAI and news sources.
        </p>

        {/* Search bar */}
        <div style={{ maxWidth: '460px', display: 'flex', marginBottom: '8px' }}>
          <input
            type="text"
            placeholder="city_name"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{
              flex: 1,
              background: 'var(--bg-3)',
              border: '1px solid var(--line-2)',
              borderRight: 'none',
              padding: '14px 18px',
              fontFamily: 'var(--font-mono)',
              fontSize: '12px',
              color: 'var(--text)',
              outline: 'none',
              transition: 'border-color 150ms, background 150ms',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--line-3)';
              e.target.style.background = 'var(--bg-4)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--line-2)';
              e.target.style.background = 'var(--bg-3)';
            }}
          />
          <button
            onClick={handleSearch}
            style={{
              background: 'var(--red)',
              border: 'none',
              color: '#fff',
              fontFamily: 'var(--font-body)',
              fontSize: '11px',
              fontWeight: 600,
              letterSpacing: '2px',
              textTransform: 'uppercase',
              padding: '14px 24px',
              cursor: 'pointer',
              transition: 'opacity 150ms',
            }}
            onMouseEnter={(e) => (e.target.style.opacity = '0.82')}
            onMouseLeave={(e) => (e.target.style.opacity = '1')}
          >
            ANALYSE
          </button>
        </div>

        {/* Keyboard hint */}
        <div
          style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '9px',
            color: 'var(--text-4)',
            letterSpacing: '1px',
            marginTop: '8px',
          }}
        >
          press enter to analyse
        </div>

        {/* SECTION 2 — Metrics strip */}
        <div
          style={{
            marginTop: '52px',
            borderTop: '1px solid var(--line)',
            padding: '20px 0 0',
            display: 'flex',
            gap: '40px',
          }}
        >
          {[
            { value: '30+', unit: '', label: 'Cities' },
            { value: '94', unit: '%', label: 'NLP' },
            { value: '0.88', unit: '', label: 'R²' },
            { value: '6', unit: 'H', label: 'Cycle' },
          ].map((metric, idx) => (
            <div key={idx} style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
              <span
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '32px',
                  letterSpacing: '1px',
                  color: 'var(--text)',
                }}
              >
                {metric.value}
              </span>
              {metric.unit && (
                <span
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '11px',
                    color: 'var(--red)',
                  }}
                >
                  {metric.unit}
                </span>
              )}
              <div style={{ marginLeft: '8px' }}>
                <div
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '9px',
                    color: 'var(--text-3)',
                    letterSpacing: '1.5px',
                    textTransform: 'uppercase',
                  }}
                >
                  {metric.label}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* SECTION 3 — Feature table */}
        <div style={{ marginTop: '48px', borderTop: '1px solid var(--line)', paddingTop: '32px', paddingBottom: '80px' }}>
          <div className="label" style={{ marginBottom: '20px' }}>
            // system capabilities
          </div>

          {[
            {
              name: 'XGBoost Prediction',
              desc: 'ML model trained on FSSAI complaint data predicts adulteration risk 0–100 per city and food item with confidence scoring.',
            },
            {
              name: 'SHAP Explainability',
              desc: 'Every risk prediction is accompanied by a full feature breakdown showing exactly which factors drove the score up or down.',
            },
            {
              name: 'BERT NLP Extraction',
              desc: 'Transformer-based language model extracts city, food item, adulterant, and severity from raw news and complaint text at 94% accuracy.',
            },
          ].map((feature, idx) => (
            <div
              key={idx}
              style={{
                display: 'grid',
                gridTemplateColumns: '200px 1fr',
                padding: '16px 0',
                borderBottom: '1px solid var(--line)',
                gap: '40px',
              }}
            >
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  color: 'var(--red)',
                  letterSpacing: '1px',
                }}
              >
                {feature.name}
              </div>

              <div
                style={{
                  fontFamily: 'var(--font-body)',
                  fontSize: '13px',
                  fontWeight: 300,
                  color: 'var(--text-2)',
                  lineHeight: 1.8,
                }}
              >
                {feature.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
