import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function SearchBar() {
  const [city, setCity] = useState('');
  const navigate = useNavigate();

  const handleSearch = (e) => {
    e.preventDefault();
    if (city.trim()) {
      navigate(`/results?city=${encodeURIComponent(city)}`);
    }
  };

  return (
    <form onSubmit={handleSearch} style={{ marginTop: '40px' }}>
      <div
        style={{
          display: 'flex',
          gap: '0',
          width: '520px',
          height: '52px',
          backgroundColor: 'var(--bg-secondary)',
          border: '1px solid var(--border-bright)',
          borderRadius: '6px',
          overflow: 'hidden',
          transition: 'border-color 200ms cubic-bezier(0.4, 0, 0.2, 1)',
        }}
        onFocus={(e) => {
          e.currentTarget.style.borderColor = 'var(--accent-blue)';
          e.currentTarget.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
        }}
        onBlur={(e) => {
          e.currentTarget.style.borderColor = 'var(--border-bright)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        <input
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          placeholder="Enter city — Trichy, Coimbatore, Mumbai..."
          style={{
            flex: 1,
            backgroundColor: 'transparent',
            border: 'none',
            color: 'var(--text-primary)',
            fontFamily: "'Inter', sans-serif",
            fontSize: '14px',
            paddingLeft: '16px',
            paddingRight: '16px',
            outline: 'none',
          }}
        />
        <button
          type="submit"
          style={{
            backgroundColor: 'var(--accent-blue)',
            border: 'none',
            color: 'white',
            fontFamily: "'Inter', sans-serif",
            fontSize: '13px',
            fontWeight: 500,
            padding: '8px 16px',
            marginRight: '8px',
            marginTop: '8px',
            marginBottom: '8px',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            transition: 'opacity 150ms cubic-bezier(0.4, 0, 0.2, 1)',
          }}
          onMouseEnter={(e) => {
            e.target.style.opacity = '0.85';
          }}
          onMouseLeave={(e) => {
            e.target.style.opacity = '1';
          }}
        >
          Search
          <ArrowRight size={14} />
        </button>
      </div>

      <div style={{ marginTop: '12px', textAlign: 'center' }}>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '11px',
            color: 'var(--text-muted)',
          }}
        >
          Press ⌘K to search
        </span>
      </div>
    </form>
  );
}
