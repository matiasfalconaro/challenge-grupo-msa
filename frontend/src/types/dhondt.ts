//Type definitions for D'Hondt calculation system.

export interface ListInput {
  name: string;
  votes: number;
}

export interface ListResult {
  name: string;
  votes: number;
  seats: number;
}

export interface CalculationResult {
  total_seats: number;
  total_votes: number;
  results: ListResult[];
  calculation_id?: string | null;
}

// Types for aggregate voting workflow

export interface VotingSubmissionResponse {
  message: string;
  submission_ids: number[];
  total_submissions: number;
}

export interface VotingSubmissionItem {
  id: number;
  party_id: number;
  party_name: string;
  votes: number;
  submitted_at: string;
}

export interface AggregatedVotesResponse {
  total_submissions: number;
  aggregated_parties: ListResult[];
  total_votes: number;
}

export interface ClearSubmissionsResponse {
  message: string;
  deleted_count: number;
}

export interface CalculationHistoryItem {
  id: number;
  timestamp: string;
  total_seats: number;
  total_votes: number;
  results: ListResult[];
}
