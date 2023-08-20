'''
Custom Exception Classes for Database Commands
'''

class RestaurantNotFoundError(Exception):
    """Exception raised when a restaurant is not found in the database."""

    def __init__(self, restaurant_id):
        self.restaurant_id = restaurant_id
        super().__init__(f"Restaurant with ID {restaurant_id} not found.")

class DishNotFoundError(Exception):
    """Exception raised when a dish is not found in the database."""

    def __init__(self, dish_id):
        self.dish_id = dish_id
        super().__init__(f"Dish with ID {dish_id} not found.")

class DuplicateDishError(Exception):
    """Exception raised when attempting to add a dish that already exists in the database."""

    def __init__(self, dish_id):
        self.dish_id = dish_id
        super().__init__(f"Dish with ID {dish_id} already exists in the database.")

class DuplicateRestaurantError(Exception):
    """Exception raised when attempting to add a restaurant that already exists in the database."""

    def __init__(self, restaurant_id):
        self.restaurant_id = restaurant_id
        super().__init__(f"Restaurant with ID {restaurant_id} already exists in the database.")
        
class DatabaseQueryError(Exception):
    """
    Exception raised when a database command fails to execute.

    Attributes:
        command_description (str): A description of the database command that failed.
        reason (str): The reason the command failed (can be the exception message itself).
    """

    def __init__(self, command_description, reason):
        self.command_description = command_description
        self.reason = reason
        super().__init__(f"Failed to execute database command: {command_description}. Reason: {reason}")

class UserError(Exception):
    """
    Exception raised when a database command fails to execute.

    Attributes:
        action (str): A word describing process that failed (create/authenticate)
        reason (str): The reason the command failed (can be the exception message itself).
    """

    def __init__(self, action, id, username, password, error):
        self.action = action
        self.id = id
        self.username = username
        self.password = password
        self.error = error
        super().__init__(f"Failed to {action} user with ID: {id}, username: {username}, password: {password} because {error}")
