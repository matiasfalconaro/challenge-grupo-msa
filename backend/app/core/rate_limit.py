from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],
    storage_uri="memory://",
)


RATE_LIMITS = {
    "calculate": "10/minute",
    "save": "20/minute",
    "history": "30/minute",
    "health": "60/minute",
}


def get_rate_limit(endpoint: str) -> str:
    """
    Get rate limit for a specific endpoint.
    """
    return RATE_LIMITS.get(endpoint, "100/hour")
