export function getBackendUrl(): string {
  const backendUrl = process.env.BACKEND_URL;

  if (backendUrl) {
    return backendUrl;
  }

  return 'http://localhost:5000';
}

export function getPublicBackendUrl(): string {
  return import.meta.env.PUBLIC_BACKEND_URL || 'http://localhost:5000';
}
