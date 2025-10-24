/**
 * Application Configuration
 * Validates and exports environment variables
 */

function getRequiredEnv(key: string): string {
  const value = import.meta.env[key];
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }
  return value;
}

function getOptionalEnv(key: string, defaultValue: string): string {
  return import.meta.env[key] || defaultValue;
}

export const config = {
  // Backend URL for server-side API calls (internal Docker network)
  backendUrl: getOptionalEnv('BACKEND_URL', 'http://backend:5000'),

  // Public backend URL for client-side API calls (exposed to browser)
  publicBackendUrl: getOptionalEnv('PUBLIC_BACKEND_URL', 'http://localhost:5000'),

  // API endpoint base (for Astro API routes)
  apiUrl: '/api',

  // Site configuration
  site: {
    title: 'Calculadora D\'Hondt',
    description: 'Sistema de cálculo de distribución de escaños mediante el método D\'Hondt',
  }
} as const;

// Validate configuration on module load
export function validateConfig(): void {
  console.log('Configuration loaded:');
  console.log('- Backend URL:', config.backendUrl);
  console.log('- Public Backend URL:', config.publicBackendUrl);
  console.log('- API URL:', config.apiUrl);
}
