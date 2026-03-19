import { Fragment, useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getTopRisks, getRiskExplanation, getAlerts } from '../api/axios';
import LiveFeed from '../components/LiveFeed';
import IndiaMap from '../components/IndiaMap';

export default function Results() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const city = searchParams.get('city');

  const [risks, setRisks] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expandedIdx, setExpandedIdx] = useState(null);
  const [shapData, setShapData] = useState({});
  const [shapLoading, setShapLoading] = useState({});
  const [shapError, setShapError] = useState({});

  useEffect(() => {
    if (!city) {
      navigate('/');
      return;
    }

    const fetch = async () => {
      setLoading(true);
      const { data: risksData } = await getTopRisks(city);
      const { data: alertsData } = await getAlerts(city);

      setRisks(risksData || []);
      setAlerts(alertsData || []);
      setLoading(false);
    };

    fetch();
  }, [city, navigate]);

  const expandRow = async (idx) => {
    if (expandedIdx === idx) {
      setExpandedIdx(null);
      return;
    }

    if (!shapData[idx] && risks[idx]) {
      setShapLoading((prev) => ({ ...prev, [idx]: true }));
      setShapError((prev) => ({ ...prev, [idx]: false }));

      const { data: explanation, error } = await getRiskExplanation(city, risks[idx].food_item);
      if (error || !explanation) {
        setShapError((prev) => ({ ...prev, [idx]: true }));
      } else {
        setShapData((prev) => ({ ...prev, [idx]: explanation }));
      }

      setShapLoading((prev) => ({ ...prev, [idx]: false }));
    }

    setExpandedIdx(idx);
  };

  if (!city) return null;

  const getRiskColor = (score) => {
    if (score > 70) return 'var(--red)';
    if (score >= 40) return 'var(--amber)';
    return 'var(--teal)';
  };

  const getRiskLevel = (score) => {
    if (score > 70) return 'CRITICAL';
    if (score >= 40) return 'HIGH RISK';
    if (score >= 20) return 'MEDIUM';
    return 'LOW RISK';
  };

  return (
    <div className="page layout" style={{ background: 'var(--bg)', minHeight: '100vh' }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', height: 'calc(100vh - 50px)', gap: 0 }}>
        {/* LEFT COLUMN — Risk Table */}
        <div style={{ padding: '32px 40px', overflowY: 'auto' }}>
          {/* Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-end',
              paddingBottom: '20px',
              borderBottom: '1px solid var(--line)',
              marginBottom: '24px',
            }}
          >
            <div>
              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '9px',
                  color: 'var(--text-3)',
                  letterSpacing: '1.5px',
                  marginBottom: '8px',
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                }}
                onClick={() => navigate('/')}
              >
                ← BACK
              </div>

              <h1
                style={{
                  fontFamily: 'var(--font-display)',
                  fontSize: '28px',
                  letterSpacing: '2px',
                  color: 'var(--text)',
                  marginBottom: '8px',
                  textTransform: 'capitalize',
                }}
              >
                {city}
              </h1>

              <div
                style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '10px',
                  color: 'var(--text-3)',
                  letterSpacing: '1px',
                }}
              >
                Tamil Nadu · Updated 6 hours ago
              </div>
            </div>

            <div
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '10px',
                color: 'var(--red)',
                letterSpacing: '1px',
              }}
            >
              {risks.length} risk vectors identified
            </div>
          </div>

          {/* Loading state */}
          {loading && (
            <div style={{ padding: '40px 0', textAlign: 'center' }}>
              <div className="skeleton" style={{ height: '40px', marginBottom: '16px' }} />
              <div className="skeleton" style={{ height: '40px' }} />
            </div>
          )}

          {/* Risk Table */}
          {!loading && risks.length > 0 && (
            <table style={{ width: '100%', tableLayout: 'fixed' }}>
              <thead>
                <tr
                  style={{
                    fontFamily: 'var(--font-mono)',
                    fontSize: '9px',
                    color: 'var(--text-4)',
                    letterSpacing: '2px',
                    textTransform: 'uppercase',
                    fontWeight: 400,
                    borderBottom: '1px solid var(--line-2)',
                    paddingBottom: '10px',
                  }}
                >
                  <th style={{ width: '32px', textAlign: 'left' }}>#</th>
                  <th style={{ width: '180px', textAlign: 'left', paddingRight: '16px' }}>ITEM</th>
                  <th style={{ width: '160px', textAlign: 'left', paddingRight: '16px' }}>ADULTERANT</th>
                  <th style={{ textAlign: 'left', paddingRight: '16px', minWidth: '120px' }}>RISK LEVEL</th>
                  <th style={{ width: '100px', textAlign: 'right', paddingRight: '16px' }}>SCORE</th>
                  <th style={{ width: '80px', textAlign: 'right' }}>REPORTS</th>
                </tr>
              </thead>
              <tbody>
                {risks.map((risk, idx) => {
                  const color = getRiskColor(risk.risk_score);
                  const level = getRiskLevel(risk.risk_score);
                  const isExpanded = expandedIdx === idx;

                  return (
                    <Fragment key={`row-${idx}`}>
                      {/* Main row */}
                      <tr
                        style={{
                          borderBottom: '1px solid var(--line)',
                          cursor: 'pointer',
                          transition: 'background 150ms',
                          background: isExpanded ? 'var(--bg-2)' : 'transparent',
                        }}
                        onClick={() => expandRow(idx)}
                        onMouseEnter={(e) => {
                          if (!isExpanded) e.currentTarget.style.background = 'var(--bg-2)';
                        }}
                        onMouseLeave={(e) => {
                          if (!isExpanded) e.currentTarget.style.background = 'transparent';
                        }}
                      >
                        <td style={{ padding: '16px 0', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--text-4)' }}>
                          {idx + 1}
                        </td>

                        <td style={{ padding: '16px 0 16px 16px', fontFamily: 'var(--font-body)', fontSize: '15px', fontWeight: 600, color: 'var(--text)', textTransform: 'capitalize' }}>
                          {risk.food_item}
                        </td>

                        <td style={{ padding: '16px 0', fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-3)', letterSpacing: '1px', textTransform: 'uppercase' }}>
                          {risk.adulterant}
                        </td>

                        <td style={{ padding: '16px 0', width: '200px' }}>
                          <div
                            className="bar-track"
                            style={{
                              '--w': `${Math.min(100, (risk.risk_score / 100) * 100)}%`,
                            }}
                          >
                            <div
                              className={`bar-fill ${
                                risk.risk_score > 70 ? 'bar-red' : risk.risk_score >= 40 ? 'bar-amber' : 'bar-teal'
                              }`}
                            />
                          </div>
                        </td>

                        <td style={{ padding: '16px 0', textAlign: 'right', paddingRight: '16px' }}>
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '20px', fontWeight: 500, color: color }}>
                            {risk.risk_score.toFixed(0)}
                          </div>
                          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '8px', color: color, opacity: 0.5, letterSpacing: '1.5px', textTransform: 'uppercase' }}>
                            {level}
                          </div>
                        </td>

                        <td style={{ padding: '16px 0', textAlign: 'right', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-3)' }}>
                          {risk.complaint_count || 0}
                        </td>
                      </tr>

                      {/* SHAP Panel */}
                      <tr
                        style={{
                          maxHeight: isExpanded ? '300px' : 0,
                          overflow: 'hidden',
                          transition: 'max-height 400ms cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                      >
                        <td colSpan="6">
                          <div
                            style={{
                              background: 'var(--bg-2)',
                              borderBottom: '1px solid var(--line)',
                              padding: '20px 32px 20px 40px',
                              marginTop: isExpanded ? 0 : '-1px',
                            }}
                          >
                            {/* Header */}
                            <div
                              style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                marginBottom: '16px',
                              }}
                            >
                              <span className="label">PREDICTION BREAKDOWN</span>
                              <div
                                style={{
                                  fontFamily: 'var(--font-mono)',
                                  fontSize: '9px',
                                  color: 'var(--teal)',
                                  border: '1px solid rgba(0, 200, 150, 0.25)',
                                  padding: '2px 8px',
                                }}
                              >
                                {Math.round(shapData[idx]?.confidence ?? 85)}% CONFIDENT
                              </div>
                            </div>

                            {/* Features */}
                            {shapLoading[idx] ? (
                              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-4)' }}>
                                // fetching explanation
                              </div>
                            ) : shapError[idx] ? (
                              <div style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-4)' }}>
                                // explanation unavailable
                              </div>
                            ) : (() => {
                              const features = shapData[idx]?.shap_data?.features || [];

                              if (features.length === 0) {
                                return (
                                  <div className="shap-empty" style={{ fontFamily: 'var(--font-body)', fontSize: '12px', color: 'var(--text-2)' }}>
                                    {shapData[idx]?.explanation_text || '// insufficient data for breakdown'}
                                  </div>
                                );
                              }

                              return (
                                <div>
                                  {features.map((feat, fidx) => {
                                    const shapValue = Number(feat.shap_value ?? feat.value ?? 0);
                                    const barWidth = Math.min(100, Math.abs(shapValue) * 100);

                                    return (
                                  <div
                                    key={fidx}
                                    style={{
                                      display: 'grid',
                                      gridTemplateColumns: '160px 1fr 60px',
                                      gap: '16px',
                                      padding: '7px 0',
                                      borderBottom: '1px solid var(--line)',
                                      alignItems: 'center',
                                    }}
                                  >
                                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-3)', letterSpacing: '1px' }}>
                                      {feat.name}
                                    </div>

                                    <div style={{ height: '1px', background: 'var(--line-2)', width: '100%' }}>
                                      <div
                                        style={{
                                          height: '100%',
                                          background: shapValue > 0 ? 'var(--red)' : 'var(--teal)',
                                          width: `${barWidth}%`,
                                        }}
                                      />
                                    </div>

                                    <div
                                      style={{
                                        fontFamily: 'var(--font-mono)',
                                        fontSize: '10px',
                                        color: shapValue > 0 ? 'var(--red)' : 'var(--teal)',
                                        textAlign: 'right',
                                      }}
                                    >
                                      {shapValue > 0 ? '+' : ''}{shapValue.toFixed(2)}
                                    </div>
                                  </div>
                                    );
                                  })}
                                </div>
                              );
                            })()}

                            {/* Explanation */}
                            <div
                              style={{
                                marginTop: '14px',
                                paddingTop: '12px',
                                borderTop: '1px solid var(--line)',
                                fontFamily: 'var(--font-body)',
                                fontSize: '12px',
                                fontWeight: 300,
                                color: 'var(--text-2)',
                                lineHeight: 1.8,
                                fontStyle: 'italic',
                                maxWidth: '560px',
                              }}
                            >
                              {shapData[idx]?.explanation_text || 'This food item shows elevated risk primarily due to recent complaints and adulterant patterns.'}
                            </div>
                          </div>
                        </td>
                      </tr>
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          )}

          {/* No data state */}
          {!loading && risks.length === 0 && (
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-4)', padding: '40px 0', textAlign: 'center' }}>
              // no data returned for this city
            </div>
          )}

          {/* Divider & Map */}
          <div style={{ marginTop: '40px' }}>
            <div className="divider" style={{ marginBottom: '32px' }} />

            <div className="label" style={{ marginBottom: '16px' }}>
              // regional context
            </div>

            <div style={{ height: '260px', background: 'var(--bg-2)', border: '1px solid var(--line)' }}>
              <IndiaMap height="260px" zoom={5} />
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN — Live Feed */}
        <div>
          <LiveFeed city={city} alerts={alerts} />
        </div>
      </div>

      {/* Fixed Report Button */}
      <button
        onClick={() => navigate(`/report?city=${encodeURIComponent(city)}`)}
        style={{
          position: 'fixed',
          bottom: '28px',
          right: '32px',
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          letterSpacing: '2px',
          textTransform: 'uppercase',
          background: 'var(--red)',
          color: '#fff',
          padding: '12px 20px',
          border: 'none',
          cursor: 'pointer',
          fontWeight: 500,
          transition: 'opacity 150ms, transform 150ms',
        }}
        onMouseEnter={(e) => {
          e.target.style.opacity = '0.85';
          e.target.style.transform = 'translateY(-1px)';
        }}
        onMouseLeave={(e) => {
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
        }}
      >
        REPORT INCIDENT
      </button>
    </div>
  );
}
