/**
 * Environment variable utilities for server-side code
 * This helper ensures environment variables are accessible in all contexts
 */

/**
 * Detect if we're running inside a Docker container
 * This is needed because the backend URL differs between Docker and local dev
 */
function isRunningInDocker(): boolean {
  // Check for Docker-specific environment indicators
  try {
    // Most reliable: check if /.dockerenv exists (standard Docker marker)
    if (typeof process !== 'undefined') {
      const fs = require('fs');
      if (fs.existsSync('/.dockerenv')) {
        return true;
      }
    }
  } catch (e) {
    // Ignore errors
  }

  // Fallback: check if 'backend' hostname is set in BACKEND_URL
  // If explicitly using 'backend' hostname, assume Docker
  const backendUrl = process.env.BACKEND_URL || '';
  if (backendUrl.includes('backend:')) {
    return true;
  }

  return false;
}

// Access Node.js environment variables directly
// This works in SSR and API routes since Astro with @astrojs/node adapter runs in Node.js
const IS_DOCKER = isRunningInDocker();

// Smart backend URL selection:
// - Inside Docker: use 'http://backend:5000' (container-to-container communication)
// - Outside Docker (dev): use 'http://localhost:5000' (host-to-host communication)
const BACKEND_URL = process.env.BACKEND_URL ||
                    (IS_DOCKER ? 'http://backend:5000' : 'http://localhost:5000');

const PUBLIC_BACKEND_URL = process.env.PUBLIC_BACKEND_URL || 'http://localhost:5000';

/**
 * Get the backend URL for server-side API calls
 * This function works in both SSR pages and API routes
 * Automatically detects Docker vs local dev environment
 */
export function getBackendUrl(): string {
  return BACKEND_URL;
}

/**
 * Get the public backend URL for client-side API calls
 */
export function getPublicBackendUrl(): string {
  return PUBLIC_BACKEND_URL;
}
