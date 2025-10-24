import type { APIRoute } from 'astro';
import { getBackendUrl } from '../../utils/env';

// Disable prerendering for this API route
export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  try {
    const backendUrl = getBackendUrl();
    const data = await request.json();

    const response = await fetch(`${backendUrl}/calculate-aggregate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
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
        detail: error instanceof Error ? error.message : 'Failed to calculate aggregate',
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
