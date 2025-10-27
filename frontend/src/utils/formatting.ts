export function formatDate(date: Date): string {
  return date.toLocaleDateString('es-AR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

export function formatTime(date: Date): string {
  return date.toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

export function formatNumber(num: number): string {
  return num.toLocaleString();
}

export function formatPercentage(value: number, total: number, decimals: number = 2): string {
  if (total === 0) return '0.00%';
  return ((value / total) * 100).toFixed(decimals) + '%';
}
