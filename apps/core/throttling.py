from rest_framework.throttling import ScopedRateThrottle


class ScopedApiThrottle(ScopedRateThrottle):
    """Base class for API throttles using scoped rates from settings."""
