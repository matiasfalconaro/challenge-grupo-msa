import type { APIRoute } from 'astro';
import { DhondtApiService } from '../../services/api';

export const POST: APIRoute = async ({ request, redirect }) => {
  try {
    const formData = await request.formData();
    const resultData = formData.get('resultData') as string;

    if (!resultData) {
      return new Response(JSON.stringify({ error: 'No se proporcionaron datos' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' }
      });
    }

    const data = JSON.parse(resultData);

    // Save using the API service
    await DhondtApiService.save(data);

    // Redirect to history page
    return redirect('/history', 303);
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
};
