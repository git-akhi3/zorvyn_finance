from apps.core.throttling import ScopedApiThrottle


class RegisterThrottle(ScopedApiThrottle):
    scope = 'auth_register'


class LoginThrottle(ScopedApiThrottle):
    scope = 'auth_login'


class UsersReadThrottle(ScopedApiThrottle):
    scope = 'users_read'


class UsersWriteThrottle(ScopedApiThrottle):
    scope = 'users_write'
