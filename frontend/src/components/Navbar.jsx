export default function Navbar() {
  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-green-600">🥬</span>
            <span className="text-xl font-bold text-gray-800">PureCheck</span>
          </div>
          <p className="text-sm text-gray-600">Real-Time Food Safety Intelligence</p>
        </div>
      </div>
    </nav>
  );
}
