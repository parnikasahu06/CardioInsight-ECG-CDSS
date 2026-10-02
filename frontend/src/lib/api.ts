import { ECGPredictionResponse } from '@/types/ecg';

let activeBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://cardioinsight-ecg-cdss.onrender.com';

async function getWorkingBaseUrl(): Promise<string> {
  const candidates = [
    process.env.NEXT_PUBLIC_API_URL,
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://cardioinsight-ecg-cdss.onrender.com',
  ].filter(Boolean) as string[];

  for (const url of candidates) {
    try {
      const res = await fetch(`${url}/health`, { method: 'GET', cache: 'no-store' });
      if (res.ok) {
        activeBaseUrl = url;
        return url;
      }
    } catch (e) {
      // continue to next candidate
    }
  }

  return activeBaseUrl;
}

export async function uploadECGFiles(heaFile: File, datFile: File): Promise<ECGPredictionResponse> {
  if (!heaFile || !datFile) {
    throw new Error('Missing files: Please select both a WFDB header (.hea) and binary signal data (.dat) file.');
  }

  if (!heaFile.name.toLowerCase().endsWith('.hea')) {
    throw new Error(`Invalid file type: Header file '${heaFile.name}' must have a .hea extension.`);
  }

  if (!datFile.name.toLowerCase().endsWith('.dat')) {
    throw new Error(`Invalid file type: Signal data file '${datFile.name}' must have a .dat extension.`);
  }

  const heaStem = heaFile.name.substring(0, heaFile.name.lastIndexOf('.')) || heaFile.name;
  const datStem = datFile.name.substring(0, datFile.name.lastIndexOf('.')) || datFile.name;
  if (heaStem !== datStem) {
    throw new Error(
      `Filename mismatch: Header file '${heaFile.name}' does not match signal file '${datFile.name}'. Both files must share the exact same record name (e.g., '${heaStem}.hea' and '${heaStem}.dat').`
    );
  }

  let baseUrl = activeBaseUrl;
  try {
    baseUrl = await getWorkingBaseUrl();
  } catch (e) {
    // fallback
  }

  const formData = new FormData();
  formData.append('hea_file', heaFile);
  formData.append('dat_file', datFile);

  try {
    const response = await fetch(`${baseUrl}/predict`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: null }));
      const detail = errorData.detail || errorData.message;
      if (detail) {
        throw new Error(detail);
      }
      throw new Error(`Server returned error HTTP ${response.status}: ${response.statusText}`);
    }

    const data: ECGPredictionResponse = await response.json();

    if (data.error) {
      throw new Error(data.error);
    }

    return data;
  } catch (error: any) {
    console.error('API call failed:', error);

    const msg = error.message || '';
    if (msg.includes('Failed to fetch') || msg.includes('NetworkError') || msg.includes('Load failed')) {
      throw new Error(
        `Backend Offline: Unable to reach the ECG Analysis Server (${baseUrl}). Please verify that the FastAPI backend is running.`
      );
    }

    throw new Error(msg || 'Failed to process and analyze the ECG record.');
  }
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const baseUrl = await getWorkingBaseUrl();
    const response = await fetch(`${baseUrl}/health`, {
      method: 'GET',
      cache: 'no-store',
      headers: { 'Cache-Control': 'no-cache' }
    });
    if (response.ok) {
      const data = await response.json();
      return data.status === 'healthy';
    }
    return false;
  } catch (error) {
    return false;
  }
}

