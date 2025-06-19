# Define user roles for the application
class UserRole:
    ADMIN_ID = 1         # The unique ID for the admin user in the database
    ADMIN = 'admin'      # String identifier for admin role
    VOTER = 'voter'      # String identifier for voter role

# Define possible account statuses for users
class AccountStatus:
    ACTIVE = True        # Account is active and can participate
    BLOCKED = False      # Account is blocked from participation

# Define possible election visibility statuses
class ElectionStatus:
    PUBLIC = True        # Election results are public
    PRIVATE = False      # Election results are private