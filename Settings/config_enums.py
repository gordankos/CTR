
from enum import Enum


class ConfirmationCategory(Enum):
    ADD_NEW_DATE = "Add new date"
    SAVE_BEFORE_CLOSE = "Save unsaved data"
    REMOVE_SERVING = "Remove Serving"
    REMOVE_DAILY_INTAKE = "Remove Daily Intake"
    REMOVE_RECIPE = "Remove Recipe"
    REMOVE_RECIPE_INGREDIENT = "Remove Recipe Ingredient"
    REMOVE_PRODUCT = "Remove Product"
    OVERRIDE_DAILY_INTAKE = "Override Daily Intake Data"
    OTHER = "Other"


class DialogWindow(Enum):
    CONFIRM_ACTION = "Confirm Action"
    CONFIRM_QUIT = "Confirm Quit"
    ERROR = "Error"
