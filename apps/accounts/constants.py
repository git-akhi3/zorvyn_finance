class AuthMessages:
    REGISTER_SUCCESS = "Account created successfully."
    LOGIN_SUCCESS = "Login successful."
    LOGOUT_SUCCESS = "Logged out successfully."
    INVALID_CREDENTIALS = "Invalid email or password."
    ACCOUNT_INACTIVE = "Your account has been deactivated."
    ROLE_SEED_MISSING = "Role seed data missing. Run seeders before registering users."
    EMAIL_REQUIRED = "Email is required."


class AuthErrorCodes:
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_INACTIVE = "account_inactive"
    ALREADY_EXISTS = "already_exists"
    CANNOT_DEACTIVATE_SELF = "cannot_deactivate_self"


class UserMessages:
    USER_FETCHED = "User retrieved successfully."
    USERS_FETCHED = "Users retrieved successfully."
    USER_UPDATED = "User updated successfully."
    CANNOT_DEACTIVATE_SELF = "You cannot deactivate your own account."
    USER_NOT_FOUND = "User not found."
    ROLE_NOT_FOUND = "Role not found."


class RoleMessages:
    ROLES_FETCHED = "Roles retrieved successfully."


class PermissionMessages:
    ADMIN_ONLY = "Only admins can perform this action."
    ANALYST_OR_ABOVE = "Analysts and admins can perform this action."
    VIEWER_OR_ABOVE = "All authenticated users can perform this action."
    ADMIN_WRITE_ONLY = "Only admins can modify data."


class CommonMessages:
    VALIDATION_ERROR = "Validation failed."


class RoleConfig:
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"

    ROLE_METADATA = {
        VIEWER: {
            "label": "Viewer",
            "description": "Can only view dashboard data.",
        },
        ANALYST: {
            "label": "Analyst",
            "description": "Can view records and access insights.",
        },
        ADMIN: {
            "label": "Admin",
            "description": "Full access to manage records and users.",
        },
    }

    ROLE_CHOICES = [(name, item["label"]) for name, item in ROLE_METADATA.items()]
