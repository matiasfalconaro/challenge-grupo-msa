import type { APIRoute } from 'astro';

export const POST: APIRoute = async ({ request }) => {
  try {
    const backendUrl = import.meta.env.BACKEND_URL || 'http://backend:5000';
    const data = await request.json();

    const response = await fetch(`${backendUrl}/submit-votes`, {
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
        detail: error instanceof Error ? error.message : 'Failed to submit votes',
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
