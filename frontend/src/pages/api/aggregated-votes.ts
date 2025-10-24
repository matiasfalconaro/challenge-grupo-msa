import type { APIRoute } from 'astro';

export const GET: APIRoute = async () => {
  try {
    const backendUrl = import.meta.env.BACKEND_URL || 'http://backend:5000';

    const response = await fetch(`${backendUrl}/aggregated-votes`);
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
        detail: error instanceof Error ? error.message : 'Failed to get aggregated votes',
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
