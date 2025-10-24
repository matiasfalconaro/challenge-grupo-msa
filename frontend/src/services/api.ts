import type {
  CalculationResult,
  ListInput,
  VotingSubmissionResponse,
  AggregatedVotesResponse,
  ClearSubmissionsResponse,
  CalculationHistoryItem
} from '../types/dhondt';

// Use Astro API endpoints instead of direct backend calls
// This provides better security and CORS management
const getApiUrl = () => {
  // Always use relative API endpoints which will be proxied by Astro
  return '/api';
};

const API_URL = getApiUrl();

export class DhondtApiService {

  // AGGREGATE VOTING API METHODS

  //Submit voting data to database for aggregation.
  static async submitVotes(lists: ListInput[]): Promise<VotingSubmissionResponse> {
    const response = await fetch(`${API_URL}/submit-votes`, {
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
    const response = await fetch(`${API_URL}/aggregated-votes`);

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
    const response = await fetch(`${API_URL}/calculate-aggregate`, {
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
    const response = await fetch(`${API_URL}/clear-submissions`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to clear submissions');
    }

    return await response.json();
  }

  //Get calculation history.
  static async getCalculationHistory(limit: number = 20): Promise<CalculationHistoryItem[]> {
    const response = await fetch(`${API_URL}/calculation-history?limit=${limit}`);

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Failed to load calculation history');
    }

    return await response.json();
  }
}
