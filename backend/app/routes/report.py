from datetime import datetime
from fastapi import (APIRouter,
                     HTTPException,
                     Request,
                     Query)
from fastapi.responses import StreamingResponse
from typing import Optional

from app.services.report import get_report_service
from app.core.rate_limit import (limiter,
                                 get_rate_limit)
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get('/download-report')
@limiter.limit(get_rate_limit("history"))
def download_comprehensive_report(request: Request):
    """
    Download comprehensive Excel report with all database data.
    """
    try:
        logger.info("Generating comprehensive report download")

        report_service = get_report_service()
        excel_file = report_service.generate_comprehensive_report()
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f'dhondt_comprehensive_report_{timestamp}.xlsx'

        logger.info(f"Serving report file: {filename}")

        return StreamingResponse(
            excel_file,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Access-Control-Expose-Headers': 'Content-Disposition'
            }
        )

    except RuntimeError as e:
        logger.error(f"Report generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in report download: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get('/download-custom-report')
@limiter.limit(get_rate_limit("history"))
def download_custom_report(
    request: Request,
    start_date: Optional[str] = Query(None, description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (ISO format: YYYY-MM-DD)"),
    party: Optional[str] = Query(None, description="Party name to filter by")
):
    """
    Download custom filtered Excel report.
    """
    try:
        logger.info(f"Generating custom report: start={start_date}, end={end_date}, party={party}")

        report_service = get_report_service()
        excel_file = report_service.generate_custom_report(start_date=start_date,
                                                          end_date=end_date,
                                                          party_filter=party)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filter_suffix = ""
        if party:
            filter_suffix += f"_{party.replace(' ', '_')}"
        if start_date or end_date:
            filter_suffix += f"_{start_date or 'start'}_to_{end_date or 'end'}"

        filename = f'dhondt_custom_report{filter_suffix}_{timestamp}.xlsx'

        logger.info(f"Serving custom report file: {filename}")

        return StreamingResponse(
            excel_file,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Access-Control-Expose-Headers': 'Content-Disposition'
            }
        )

    except RuntimeError as e:
        logger.error(f"Custom report generation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate custom report: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in custom report download: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
