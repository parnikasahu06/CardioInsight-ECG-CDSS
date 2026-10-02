export function formatFeatureName(name: string): string {
  if (!name) return '';
  const leadMap: Record<string, string> = {
    i: 'I', ii: 'II', iii: 'III',
    avr: 'aVR', avl: 'aVL', avf: 'aVF',
    v1: 'V1', v2: 'V2', v3: 'V3', v4: 'V4', v5: 'V5', v6: 'V6'
  };
  const acronymMap: Record<string, string> = {
    qrs: 'QRS', ecg: 'ECG', sqi: 'SQI', pr: 'PR', qt: 'QT', qtc: 'QTc', st: 'ST'
  };

  return name
    .split(/[_\s]+/)
    .map(part => {
      const lower = part.toLowerCase();
      if (leadMap[lower]) return leadMap[lower];
      if (acronymMap[lower]) return acronymMap[lower];
      if (['s', 'p', 'q', 'r', 't'].includes(lower)) return lower.toUpperCase();
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    })
    .join(' ');
}

export function formatTimestamp(ts?: string | Date): string {
  if (!ts) return new Date().toLocaleString() + ' IST (UTC+5:30)';

  if (typeof ts === 'string' && ts.includes('IST (UTC+5:30)')) {
    return ts;
  }

  let date: Date;
  if (ts instanceof Date) {
    date = ts;
  } else if (typeof ts === 'string') {
    let str = ts.trim();
    if (/^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}$/.test(str)) {
      str = str.replace(' ', 'T') + 'Z';
    }
    date = new Date(str);
    if (isNaN(date.getTime())) {
      date = new Date(ts);
    }
  } else {
    date = new Date();
  }

  if (isNaN(date.getTime())) {
    return String(ts) + ' IST (UTC+5:30)';
  }

  try {
    const parts = new Intl.DateTimeFormat('en-CA', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      timeZone: 'Asia/Kolkata',
    }).formatToParts(date);

    const p: Record<string, string> = {};
    parts.forEach(part => { p[part.type] = part.value; });
    return `${p.year}-${p.month}-${p.day} ${p.hour}:${p.minute}:${p.second} IST (UTC+5:30)`;
  } catch {
    return date.toLocaleString() + ' IST (UTC+5:30)';
  }
}
