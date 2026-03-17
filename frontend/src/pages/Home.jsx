import { useNavigate } from 'react-router-dom';
import SearchBar from '../components/SearchBar';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    {
      icon: '📊',
      title: 'Real-Time Risk Scores',
      description: 'ML-powered predictions updated every 6 hours with fresh data'
    },
    {
      icon: '📰',
      title: 'Multi-Source Intelligence',
      description: 'Aggregates FSSAI reports, news articles, and citizen complaints'
    },
    {
      icon: '🚨',
      title: 'Live Alerts',
      description: 'Instant WebSocket notifications when high-risk items detected'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="mb-8">
          <span className="text-6xl">🥬</span>
        </div>
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          PureCheck
        </h1>
        <p className="text-2xl text-orange-600 font-semibold mb-2">
          Know what's risky before you buy
        </p>
        <p className="text-lg text-gray-600 mb-12 max-w-2xl mx-auto">
          Real-Time Food Adulteration Risk Intelligence for Indian Markets
        </p>

        {/* Search Bar */}
        <div className="flex justify-center mb-16">
          <SearchBar />
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mt-12">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
            >
              <span className="text-4xl mb-4 block">{feature.icon}</span>
              <h3 className="text-xl font-bold text-gray-800 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-600">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Footer Info */}
        <div className="mt-16 pt-8 border-t border-gray-200">
          <p className="text-gray-600">
            <span className="font-semibold">Covering Cities:</span> Trichy, Coimbatore, Chennai, Madurai, Salem, and more
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Data updated every 6 hours • Powered by ML and NLP
          </p>
        </div>
      </div>
    </div>
  );
}
