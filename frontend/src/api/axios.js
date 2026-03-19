import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
const TIMEOUT = 10000;

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: TIMEOUT,
});

export async function getTopRisks(city) {
  try {
    const response = await client.get('/api/risk/', {
      params: { city },
    });
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getTopRisks error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch top risks' };
  }
}

export async function getRiskExplanation(city, food) {
  try {
    const response = await client.get('/api/risk/explain/', {
      params: { city, food },
    });
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getRiskExplanation error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch risk explanation' };
  }
}

export async function getHeatmapData() {
  try {
    const response = await client.get('/api/heatmap/');
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getHeatmapData error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch heatmap data' };
  }
}

export async function getStats() {
  try {
    const response = await client.get('/api/stats/');
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getStats error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch stats' };
  }
}

export async function getAlerts(city) {
  try {
    const response = await client.get('/api/alerts/', {
      params: { city },
    });
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getAlerts error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch alerts' };
  }
}

export async function getCities() {
  try {
    const response = await client.get('/api/cities/');
    return { data: response.data, error: null };
  } catch (err) {
    console.error('getCities error:', err.message);
    return { data: null, error: err.message || 'Failed to fetch cities' };
  }
}

export async function submitReport(data) {
  try {
    const response = await client.post('/api/report/', data);
    return { data: response.data, error: null };
  } catch (err) {
    console.error('submitReport error:', err.message);
    return { data: null, error: err.message || 'Failed to submit report' };
  }
}

export async function exportToCSV() {
  try {
    const response = await fetch(
      'http://localhost:8000/api/export/',
      { method: 'GET' }
    );
    if (!response.ok) {
      throw new Error(
        `Export failed: ${response.status}`);
    }
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute(
      'download', 'purecheck_live.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export default client;
