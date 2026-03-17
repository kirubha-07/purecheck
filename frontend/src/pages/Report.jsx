import { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { riskAPI } from '../api/axios';

export default function Report() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const city = searchParams.get('city') || '';

  const [formData, setFormData] = useState({
    city: city,
    food_item: '',
    adulterant: '',
    description: ''
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.city || !formData.food_item || !formData.adulterant || !formData.description) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await riskAPI.submitReport(
        formData.city,
        formData.food_item,
        formData.adulterant,
        formData.description
      );
      setSuccess(true);
      setTimeout(() => {
        navigate(`/results?city=${encodeURIComponent(formData.city)}`);
      }, 2000);
    } catch (err) {
      setError('Failed to submit report. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-12">
        <button
          onClick={() => navigate(-1)}
          className="text-green-600 hover:text-green-700 font-semibold mb-8 flex items-center gap-1"
        >
          ← Back
        </button>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <span className="text-4xl block mb-3">📋</span>
            <h1 className="text-3xl font-bold text-gray-900">Report Food Adulteration</h1>
            <p className="text-gray-600 mt-2">
              Help us keep {formData.city} safe. Your report helps other consumers.
            </p>
          </div>

          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
              <p className="text-green-800 font-semibold">
                ✅ Thank you! Your report has been submitted and will update risk scores within minutes.
              </p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* City */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                City *
              </label>
              <input
                type="text"
                name="city"
                value={formData.city}
                onChange={handleChange}
                placeholder="e.g., Trichy"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-600"
              />
            </div>

            {/* Food Item */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Food Item *
              </label>
              <input
                type="text"
                name="food_item"
                value={formData.food_item}
                onChange={handleChange}
                placeholder="e.g., Milk, Rice, Oil"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-600"
              />
            </div>

            {/* Adulterant */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Suspected Adulterant *
              </label>
              <select
                name="adulterant"
                value={formData.adulterant}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-600"
              >
                <option value="">Select an adulterant</option>
                <option value="detergent">Detergent</option>
                <option value="starch">Starch</option>
                <option value="synthetic color">Synthetic Color</option>
                <option value="pesticide">Pesticide</option>
                <option value="chalk powder">Chalk Powder</option>
                <option value="water">Water</option>
                <option value="urea">Urea</option>
                <option value="metanil yellow">Metanil Yellow</option>
                <option value="lead chromate">Lead Chromate</option>
                <option value="other">Other</option>
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Detailed Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe what you observed, where you bought it, symptoms if any..."
                rows="6"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-600"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 transition"
            >
              {loading ? 'Submitting...' : '📤 Submit Report'}
            </button>
          </form>

          <p className="text-xs text-gray-500 text-center mt-6">
            Your report helps maintain food safety standards in your community
          </p>
        </div>
      </div>
    </div>
  );
}
