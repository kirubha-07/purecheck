import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'HOME' },
    { path: '/results', label: 'RESULTS' },
    { path: '/heatmap', label: 'HEATMAP' },
    { path: '/dashboard', label: 'DASHBOARD' },
    { path: '/report', label: 'REPORT' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <nav
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: '50px',
        background: 'var(--bg)',
        borderBottom: '1px solid var(--line)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingLeft: '40px',
        paddingRight: '40px',
      }}
    >
      {/* LEFT — Logo */}
      <Link
        to="/"
        style={{
          textDecoration: 'none',
          display: 'flex',
          alignItems: 'baseline',
          gap: 0,
          fontFamily: 'var(--font-display)',
          fontSize: '18px',
          letterSpacing: '3px',
          color: 'var(--text)',
          position: 'relative',
        }}
      >
        <span style={{ color: 'var(--red)' }}>PURE</span>
        <span>CHECK</span>
      </Link>

      {/* CENTER — Nav Links */}
      <div style={{ display: 'flex', gap: '28px', position: 'absolute', left: '50%', transform: 'translateX(-50%)' }}>
        {navLinks.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            style={{
              textDecoration: 'none',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              letterSpacing: '1.5px',
              textTransform: 'uppercase',
              color: isActive(link.path) ? 'var(--text)' : 'var(--text-3)',
              transition: 'color 150ms',
              cursor: 'pointer',
            }}
            onMouseEnter={(e) => {
              e.target.style.color = 'var(--text-2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.color = isActive(link.path) ? 'var(--text)' : 'var(--text-3)';
            }}
          >
            {link.label}
          </Link>
        ))}
      </div>

      {/* RIGHT — System Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'var(--font-mono)', fontSize: '9px', color: 'var(--text-4)', letterSpacing: '1px' }}>
        <div
          style={{
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            background: 'var(--red)',
            animation: 'pulse 1.8s ease-in-out infinite',
            flexShrink: 0,
          }}
        />
        PIPELINE ACTIVE
      </div>

      {/* Accent line */}
      <div className="accent-line" />
    </nav>
  );
}
