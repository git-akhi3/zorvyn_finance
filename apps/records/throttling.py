from apps.core.throttling import ScopedApiThrottle


class RecordsReadThrottle(ScopedApiThrottle):
    scope = 'records_read'


class RecordsWriteThrottle(ScopedApiThrottle):
    scope = 'records_write'


class DashboardReadThrottle(ScopedApiThrottle):
    scope = 'dashboard_read'
