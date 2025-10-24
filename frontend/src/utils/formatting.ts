/**
 * Formatting utilities for the application
 */

/**
 * Formats a date object to Spanish locale date string
 * @param date - Date to format
 * @returns Formatted date string (DD/MM/YYYY)
 */
export function formatDate(date: Date): string {
  return date.toLocaleDateString('es-AR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

/**
 * Formats a date object to Spanish locale time string
 * @param date - Date to format
 * @returns Formatted time string (HH:MM:SS)
 */
export function formatTime(date: Date): string {
  return date.toLocaleTimeString('es-AR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

/**
 * Formats a number with thousands separators
 * @param num - Number to format
 * @returns Formatted number string
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * Calculates percentage and formats it
 * @param value - Numerator value
 * @param total - Denominator value
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted percentage string
 */
export function formatPercentage(value: number, total: number, decimals: number = 2): string {
  if (total === 0) return '0.00%';
  return ((value / total) * 100).toFixed(decimals) + '%';
}
