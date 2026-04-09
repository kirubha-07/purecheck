import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { submitReport } from '../api/axios';

const FOODS = ['Milk', 'Rice', 'Oil', 'Wheat', 'Salt', 'Spices', 'Vegetables', 'Fruits', 'Meat', 'Seafood', 'Dairy', 'Grains', 'Condiments', 'Beverages'];

const ADULTERANTS = [
  'Detergent',
  'Starch',
  'Synthetic Color',
  'Pesticide',
  'Chalk Powder',
  'Water',
  'Urea',
  'Metanil Yellow',
  'Lead Chromate',
  'Melamine',
  'Heavy Metals',
  'Plastic',
  'Other',
];

export default function Report() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const city = searchParams.get('city') || '';

  const [formData, setFormData] = useState({
    city,
    food_item: '',
    adulterant: '',
    severity: 3,
    description: '',
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'severity' ? parseInt(value) : value,
    }));
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.city || !formData.food_item || !formData.adulterant || !formData.description) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    const { data: result, error: err } = await submitReport(formData);

    if (err) {
      setError(err);
      setLoading(false);
      return;
    }

    setSuccess(true);
    setTimeout(() => {
      navigate(`/results?city=${encodeURIComponent(formData.city)}`);
    }, 2000);
  };

  if (success) {
    return (
      <div className="page layout" style={{ background: 'var(--bg)', padding: '48px 40px', textAlign: 'center' }}>
        <div style={{ maxWidth: '520px', margin: '0 auto' }}>
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '50%',
              background: 'var(--teal)',
              margin: '0 auto 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: '20px',
            }}
          >
            ✓
          </div>

          <h1
            style={{
              fontFamily: 'var(--font-display)',
              fontSize: '24px',
              letterSpacing: '2px',
              color: 'var(--text)',
              marginBottom: '12px',
            }}
          >
            REPORT SUBMITTED
          </h1>

          <p
            style={{
              fontFamily: 'var(--font-body)',
              fontSize: '13px',
              fontWeight: 300,
              color: 'var(--text-2)',
              lineHeight: 1.8,
            }}
          >
            Risk scores for {formData.city} will be recalculated in the next pipeline run. Thank you for contributing to PureCheck.
          </p>

          <button
            onClick={() => navigate(`/results?city=${encodeURIComponent(formData.city)}`)}
            style={{
              marginTop: '24px',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              color: 'var(--text-3)',
              letterSpacing: '1.5px',
              textTransform: 'uppercase',
              background: 'transparent',
              border: '1px solid var(--line-2)',
              padding: '10px 20px',
              cursor: 'pointer',
              transition: 'border-color 150ms, color 150ms',
            }}
            onMouseEnter={(e) => {
              e.target.style.borderColor = 'var(--line-3)';
              e.target.style.color = 'var(--text-2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.borderColor = 'var(--line-2)';
              e.target.style.color = 'var(--text-3)';
            }}
          >
            ← BACK TO RESULTS
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page layout" style={{ background: 'var(--bg)', padding: '48px 40px' }}>
      <div style={{ maxWidth: '520px', margin: '0 auto' }}>
        {/* Header */}
        <div className="label" style={{ marginBottom: '12px' }}>
          // submit incident report
        </div>

        <h1
          style={{
            fontFamily: 'var(--font-display)',
            fontSize: '32px',
            letterSpacing: '2px',
            color: 'var(--text)',
            marginBottom: '12px',
          }}
        >
          REPORT AN INCIDENT
        </h1>

        <p
          style={{
            fontFamily: 'var(--font-body)',
            fontSize: '13px',
            fontWeight: 300,
            color: 'var(--text-2)',
            lineHeight: 1.8,
            marginBottom: '32px',
          }}
        >
          Your report feeds directly into the PureCheck pipeline. Verified reports are weighted in the next risk score calculation.
        </p>

        {error && (
          <div
            style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              color: 'var(--red)',
              background: 'var(--red-dim)',
              border: '1px solid var(--red-line)',
              padding: '12px 16px',
              marginBottom: '20px',
            }}
          >
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* City */}
          <div>
            <label
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                color: 'var(--text-3)',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginBottom: '6px',
                display: 'block',
              }}
            >
              City
            </label>
            <input
              type="text"
              name="city"
              value={formData.city}
              onChange={handleChange}
              placeholder="city_name"
              style={{
                width: '100%',
                background: 'var(--bg-3)',
                border: '1px solid var(--line-2)',
                borderRadius: 0,
                color: 'var(--text)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                padding: '12px 14px',
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
          </div>

          {/* Food Item */}
          <div>
            <label
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                color: 'var(--text-3)',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginBottom: '6px',
                display: 'block',
              }}
            >
              Food Item
            </label>
            <select
              name="food_item"
              value={formData.food_item}
              onChange={handleChange}
              style={{
                width: '100%',
                background: 'var(--bg-3)',
                border: '1px solid var(--line-2)',
                borderRadius: 0,
                color: 'var(--text)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                padding: '12px 14px',
                outline: 'none',
                cursor: 'pointer',
               appearance: 'none',
                backgroundImage:
                  "url(\"data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233A3A52' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e\")",
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 8px center',
                backgroundSize: '20px',
                paddingRight: '32px',
              }}
            >
              <option value="">Select food item</option>
              {FOODS.map((food) => (
                <option key={food} value={food}>
                  {food}
                </option>
              ))}
            </select>
          </div>

          {/* Adulterant */}
          <div>
            <label
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                color: 'var(--text-3)',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginBottom: '6px',
                display: 'block',
              }}
            >
              Suspected Adulterant
            </label>
            <select
              name="adulterant"
              value={formData.adulterant}
              onChange={handleChange}
              style={{
                width: '100%',
                background: 'var(--bg-3)',
                border: '1px solid var(--line-2)',
                borderRadius: 0,
                color: 'var(--text)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                padding: '12px 14px',
                outline: 'none',
                cursor: 'pointer',
                appearance: 'none',
                backgroundImage:
                  "url(\"data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233A3A52' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e\")",
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 8px center',
                backgroundSize: '20px',
                paddingRight: '32px',
              }}
            >
              <option value="">Select adulterant</option>
              {ADULTERANTS.map((adult) => (
                <option key={adult} value={adult}>
                  {adult}
                </option>
              ))}
            </select>
          </div>

          {/* Severity */}
          <div>
            <label
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                color: 'var(--text-3)',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginBottom: '8px',
                display: 'block',
              }}
            >
              Severity Level
            </label>
            <select
              name="severity"
              value={formData.severity}
              onChange={handleChange}
              style={{
                width: '100%',
                background: 'var(--bg-3)',
                border: '1px solid var(--line-2)',
                borderRadius: 0,
                color: 'var(--text)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                padding: '12px 14px',
                outline: 'none',
                cursor: 'pointer',
                appearance: 'none',
                backgroundImage:
                  "url(\"data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%233A3A52' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e\")",
                backgroundRepeat: 'no-repeat',
                backgroundPosition: 'right 8px center',
                backgroundSize: '20px',
                paddingRight: '32px',
              }}
            >
              <option value={1}>1 - Low</option>
              <option value={2}>2 - Mild</option>
              <option value={3}>3 - Moderate</option>
              <option value={4}>4 - High</option>
              <option value={5}>5 - Critical</option>
            </select>
          </div>

          {/* Description */}
          <div>
            <label
              style={{
                fontFamily: 'var(--font-mono)',
                fontSize: '9px',
                color: 'var(--text-3)',
                letterSpacing: '2px',
                textTransform: 'uppercase',
                marginBottom: '6px',
                display: 'block',
              }}
            >
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="describe what you observed..."
              rows="4"
              style={{
                width: '100%',
                background: 'var(--bg-3)',
                border: '1px solid var(--line-2)',
                borderRadius: 0,
                color: 'var(--text)',
                fontFamily: 'var(--font-mono)',
                fontSize: '12px',
                padding: '12px 14px',
                outline: 'none',
                transition: 'border-color 150ms, background 150ms',
                resize: 'vertical',
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
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              height: '46px',
              background: loading ? 'var(--text-4)' : 'var(--red)',
              border: 'none',
              color: '#fff',
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              fontWeight: 500,
              letterSpacing: '2.5px',
              textTransform: 'uppercase',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'opacity 150ms, transform 150ms',
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.opacity = '0.82';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.opacity = '1';
              }
            }}
            onMouseDown={(e) => {
              if (!loading) {
                e.target.style.transform = 'scale(0.99)';
              }
            }}
            onMouseUp={(e) => {
              if (!loading) {
                e.target.style.transform = 'scale(1)';
              }
            }}
          >
            {loading ? 'SUBMITTING...' : 'SUBMIT REPORT'}
          </button>
        </form>
      </div>
    </div>
  );
}
