import type { APIRoute } from 'astro';
import { getBackendUrl } from '../../utils/env';

// Disable prerendering for this API route
export const prerender = false;

export const DELETE: APIRoute = async () => {
  try {
    const backendUrl = getBackendUrl();

    const response = await fetch(`${backendUrl}/clear-submissions`, {
      method: 'DELETE',
    });

    const responseData = await response.json();

    return new Response(JSON.stringify(responseData), {
      status: response.status,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    return new Response(
      JSON.stringify({
        detail: error instanceof Error ? error.message : 'Failed to clear submissions',
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
