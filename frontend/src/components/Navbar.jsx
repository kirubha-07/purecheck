import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const getLinkClass = (path) => {
    const base = 'px-4 py-2 rounded-lg font-medium transition text-sm';
    return isActive(path)
      ? `${base} bg-green-100 text-green-700`
      : `${base} text-gray-700 hover:bg-gray-100`;
  };

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 hover:opacity-80 transition">
            <span className="text-2xl font-bold text-green-600">🥬</span>
            <span className="text-xl font-bold text-gray-800">PureCheck</span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center gap-2 flex-wrap">
            <Link to="/" className={getLinkClass('/')}>
              🏠 Home
            </Link>
            <Link to="/results" className={getLinkClass('/results')}>
              📊 Results
            </Link>
            <Link to="/heatmap" className={getLinkClass('/heatmap')}>
              🗺️ Risk Map
            </Link>
            <Link to="/dashboard" className={getLinkClass('/dashboard')}>
              📈 Dashboard
            </Link>
            <Link to="/report" className={getLinkClass('/report')}>
              📝 Report
            </Link>
          </div>

          {/* Tagline */}
          <p className="text-sm text-gray-600 hidden xl:block">Real-Time Food Safety</p>
        </div>
      </div>
    </nav>
  );
}
