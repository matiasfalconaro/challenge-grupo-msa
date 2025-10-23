from typing import (List,
                    Dict)
from app.models.schemas import (CalculationResponse,
                              ListResult,
                              VotingSubmissionRequest,
                              VotingSubmissionResponse,
                              VotingSubmissionItem,
                              AggregatedVotesResponse,
                              CalculateAggregateRequest,
                              ClearSubmissionsResponse,
                              CalculationHistoryItem)
from app.database import (insert_calculation,
                         get_calculation_history,
                         insert_voting_submissions,
                         get_all_voting_submissions,
                         get_aggregated_votes,
                         get_voting_submissions_count,
                         clear_all_voting_submissions)


class DhondtService:
    """Service for D'Hondt seat allocation calculations using aggregate voting workflow."""

    @staticmethod
    def _calculate_dhondt(lists: List[Dict], total_seats: int, threshold_percent: float = 3.0) -> List[Dict]:
        """
        Core D'Hondt algorithm implementation with threshold filtering.

        NOTE: threshold_percent value is set to 3.0 according to https://buenosaires.gob.ar/sites/default/files/media/document/2021/11/03/cf6fa751bd98e12d862873d24f0417820d5d6f5c.pdf
        """
        # Initialize seats for each list to 0
        results = []
        for lst in lists:
            if lst['votes'] < 0:
                raise ValueError(f"Invalid votes for {lst['name']}: votes must be non-negative")
            results.append({
                'name': lst['name'],
                'votes': lst['votes'],
                'seats': 0
            })

        # Calculate total votes
        total_votes = sum(r['votes'] for r in results)
        if total_votes == 0:
            # No votes to distribute, return all with 0 seats
            return results

        # THRESHOLD 3%
        threshold_votes = total_votes * (threshold_percent / 100)
        eligible_results = [r for r in results if r['votes'] >= threshold_votes]

        # If no list passes the threshold, return all with 0 seats
        if not eligible_results:
            return results

        # Allocate seats among eligible lists
        for _ in range(total_seats):
            max_quotient = -1
            candidates = []

            for i, result in enumerate(eligible_results):
                quotient = result['votes'] / (result['seats'] + 1)
                if quotient > max_quotient:
                    max_quotient = quotient
                    candidates = [i]
                elif quotient == max_quotient:
                    candidates.append(i)

            if candidates:
                if len(candidates) == 1:
                    eligible_results[candidates[0]]['seats'] += 1
                else:
                    # Tie-breaker: higher votes wins
                    max_votes = -1
                    winner_index = candidates[0]
                    for idx in candidates:
                        if eligible_results[idx]['votes'] > max_votes:
                            max_votes = eligible_results[idx]['votes']
                            winner_index = idx
                    eligible_results[winner_index]['seats'] += 1

        # Merge results back (non-eligible lists keep 0 seats)
        final_results = []
        eligible_names = {r['name'] for r in eligible_results}
        for r in results:
            if r['name'] in eligible_names:
                # Replace with updated data
                updated = next(er for er in eligible_results if er['name'] == r['name'])
                final_results.append(updated)
            else:
                # Keep with 0 seats
                final_results.append(r)

        return final_results

    @staticmethod
    def _save_calculation(calculation: CalculationResponse) -> str:
        """
        Internal method to save calculation result to database.
        """
        # Convert to dict
        data = calculation.model_dump()

        # Prepare results as list of dicts for JSONB storage
        results = [
            {
                'name': result['name'],
                'votes': result['votes'],
                'seats': result['seats']
            }
            for result in data['results']
        ]

        # Insert into database
        record_id = insert_calculation(
            total_seats=data['total_seats'],
            total_votes=data['total_votes'],
            results=results
        )

        return str(record_id)

    # AGGREGATE VOTING WORKFLOW METHODS
    @staticmethod
    def submit_votes(request: VotingSubmissionRequest) -> VotingSubmissionResponse:
        """
        Submit voting data to database for later aggregation.
        """
        # Prepare submissions for database
        submissions = [
            {'party_name': lst.name, 'votes': lst.votes}
            for lst in request.lists
        ]

        # Insert submissions
        submission_ids = insert_voting_submissions(submissions)

        return VotingSubmissionResponse(
            message=f'Successfully submitted votes for {len(submission_ids)} parties',
            submission_ids=submission_ids,
            total_submissions=len(submission_ids)
        )

    @staticmethod
    def get_voting_submissions(limit: int = 100) -> List[VotingSubmissionItem]:
        """
        Retrieve all voting submissions from database.
        """
        submissions = get_all_voting_submissions(limit=limit)

        return [VotingSubmissionItem(**sub) for sub in submissions]

    @staticmethod
    def get_aggregated_votes() -> AggregatedVotesResponse:
        """
        Get aggregated votes from all submissions without calculating seats.
        """
        # Get aggregated votes from database
        aggregated = get_aggregated_votes()

        # Convert to list of results
        aggregated_parties = [
            ListResult(name=party_name, votes=votes, seats=0)
            for party_name, votes in aggregated.items()
        ]

        # Sort by votes descending
        aggregated_parties.sort(key=lambda x: x.votes, reverse=True)

        total_votes = sum(party.votes for party in aggregated_parties)
        total_submissions = get_voting_submissions_count()

        return AggregatedVotesResponse(
            total_submissions=total_submissions,
            aggregated_parties=aggregated_parties,
            total_votes=total_votes
        )

    @staticmethod
    def calculate_aggregate(request: CalculateAggregateRequest) -> CalculationResponse:
        """
        Calculate D'Hondt seats on aggregated voting data from database.
        """
        # Get aggregated votes from database
        aggregated = get_aggregated_votes()

        if not aggregated:
            raise ValueError("No voting submissions found. Please submit voting data first.")

        # Convert aggregated votes to list format for D'Hondt calculation
        lists_data = [
            {'name': party_name, 'votes': votes}
            for party_name, votes in aggregated.items()
        ]

        # Perform D'Hondt calculation
        results = DhondtService._calculate_dhondt(lists_data, request.total_seats)

        total_votes = sum(r['votes'] for r in results)

        # Convert results to Pydantic models
        result_models = [
            ListResult(
                name=r['name'],
                votes=r['votes'],
                seats=r['seats']
            )
            for r in results
        ]

        calculation_response = CalculationResponse(
            total_seats=request.total_seats,
            total_votes=total_votes,
            results=result_models,
            calculation_id=None
        )

        # Save to database if requested and include calculation_id
        if request.save_result:
            calculation_id = DhondtService._save_calculation(calculation_response)
            calculation_response.calculation_id = calculation_id

        return calculation_response

    @staticmethod
    def clear_submissions() -> ClearSubmissionsResponse:
        """
        Clear all voting submissions from database.
        """
        deleted_count = clear_all_voting_submissions()

        return ClearSubmissionsResponse(
            message=f'Successfully cleared {deleted_count} voting submissions',
            deleted_count=deleted_count
        )

    @staticmethod
    def get_calculation_history(limit: int = 20) -> List[CalculationHistoryItem]:
        """
        Get calculation history from database.
        """
        history_data = get_calculation_history(limit=limit)

        # Convert to Pydantic models
        history_items = []
        for calc in history_data:
            # Convert results array to ListResult models
            results = [
                ListResult(
                    name=r['name'],
                    votes=r['votes'],
                    seats=r['seats']
                )
                for r in calc.get('results', [])
            ]

            history_items.append(
                CalculationHistoryItem(
                    id=calc['id'],
                    timestamp=calc['timestamp'],
                    total_seats=calc['total_seats'],
                    total_votes=calc['total_votes'],
                    results=results
                )
            )

        return history_items
