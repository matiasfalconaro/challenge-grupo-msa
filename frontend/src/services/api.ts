import type {
  CalculationResult,
  ListInput,
  VotingSubmissionResponse,
  AggregatedVotesResponse,
  ClearSubmissionsResponse
} from '../types/dhondt';

// Use different URLs for server-side vs client-side
// Server-side (SSR in Docker): use BACKEND_URL (http://backend:5000)
// Client-side (browser): use PUBLIC_BACKEND_URL (http://localhost:5000)
const getBackendUrl = () => {
  // Check if we're running on the server (Node.js) or client (browser)
  if (typeof window === 'undefined') {
    // Server-side: use internal Docker hostname
    return import.meta.env.BACKEND_URL || 'http://backend:5000';
  } else {
    // Client-side: use localhost for browser access
    return import.meta.env.PUBLIC_BACKEND_URL || 'http://localhost:5000';
  }
};

const BACKEND_URL = getBackendUrl();

export class DhondtApiService {

  // AGGREGATE VOTING API METHODS

  //Submit voting data to database for aggregation.
  static async submitVotes(lists: ListInput[]): Promise<VotingSubmissionResponse> {
    const response = await fetch(`${BACKEND_URL}/submit-votes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ lists }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to submit votes');
    }

    return await response.json();
  }

  //Get aggregated votes without calculating seats.
  static async getAggregatedVotes(): Promise<AggregatedVotesResponse> {
    const response = await fetch(`${BACKEND_URL}/aggregated-votes`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to get aggregated votes');
    }

    return await response.json();
  }

  //Calculate D'Hondt on aggregate data from database.
  static async calculateAggregate(
    totalSeats: number,
    saveResult: boolean = true
  ): Promise<CalculationResult> {
    const response = await fetch(`${BACKEND_URL}/calculate-aggregate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        total_seats: totalSeats,
        save_result: saveResult,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to calculate aggregate');
    }

    return await response.json();
  }

  //Clear all voting submissions from database.
  static async clearSubmissions(): Promise<ClearSubmissionsResponse> {
    const response = await fetch(`${BACKEND_URL}/clear-submissions`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to clear submissions');
    }

    return await response.json();
  }
}
