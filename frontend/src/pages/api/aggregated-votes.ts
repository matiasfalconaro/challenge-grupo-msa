import type { APIRoute } from 'astro';
import { getBackendUrl } from '../../utils/env';

// Disable prerendering for this API route
export const prerender = false;

export const GET: APIRoute = async () => {
  try {
    const backendUrl = getBackendUrl();
    console.log('[API aggregated-votes] Fetching from:', backendUrl);

    const response = await fetch(`${backendUrl}/aggregated-votes`);
    console.log('[API aggregated-votes] Response status:', response.status);

    const responseData = await response.json();
    console.log('[API aggregated-votes] Response data:', responseData);

    return new Response(JSON.stringify(responseData), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('[API aggregated-votes] Error:', error);
    return new Response(
      JSON.stringify({
        detail: error instanceof Error ? error.message : 'Failed to get aggregated votes',
        backendUrl: getBackendUrl(),
        errorStack: error instanceof Error ? error.stack : undefined
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
};
