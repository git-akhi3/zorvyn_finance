
class AuthMessages:
    REGISTER_SUCCESS = "Account created successfully."
    LOGIN_SUCCESS = "Login successful."
    LOGOUT_SUCCESS = "Logged out successfully."
    INVALID_CREDENTIALS = "Invalid email or password."
    ACCOUNT_INACTIVE = "Your account has been deactivated."


class UserMessages:
    USER_FETCHED = "User retrieved successfully."
    USERS_FETCHED = "Users retrieved successfully."
    USER_UPDATED = "User updated successfully."
    CANNOT_DEACTIVATE_SELF = "You cannot deactivate your own account."


class AuthErrorCodes:
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_INACTIVE = "account_inactive"
    ALREADY_EXISTS = "already_exists"
