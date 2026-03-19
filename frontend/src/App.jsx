import { Routes, Route, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Results from './pages/Results';
import Report from './pages/Report';
import HeatMap from './pages/HeatMap';
import Dashboard from './pages/Dashboard';

export default function App() {
  const location = useLocation();

  return (
    <div style={{ minHeight: '100vh', backgroundColor: 'var(--bg)' }}>
      <Navbar />
      <div className="page layout" style={{ paddingTop: '50px' }}>
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<Results />} />
          <Route path="/heatmap" element={<HeatMap />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/report" element={<Report />} />
        </Routes>
      </div>
    </div>
  );
}
