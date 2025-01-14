
from enum import Enum


class ServingType(Enum):
    PRODUCT = "Product"
    RECIPE = "Recipe"


class RecipeCategory(Enum):
    MAIN_COURSE = "Main Course"
    SIDE_DISH = "Side Dish"
    SALAD = "Salad"
    DESSERT = "Dessert"
    SNACK = "Snack"
    OTHER = "Other"


class ProductCategory(Enum):
    MEAT = "Meat"
    FISH = "Fish"
    VEGETABLE = "Vegetable"
    FRUIT = "Fruit"
    DAIRY = "Dairy"
    GRAIN = "Grain"
    SUPPLEMENT = "Supplement"
    OIL = "Oil"
    SOUP = "Soup"
    BEVERAGE  = "Beverage"
    CONDIMENT = "Condiment"
    SPICE = "Spice"
    SNACK = "Snack"
    FROZEN = "Frozen meal"
    OTHER = "Other"


def get_serving_type(
        name: str
) -> ServingType | None:
    """
    Returns the ServingType Enum based on the given Enum name.
    """
    return ServingType.__members__.get(name, None)


def get_recipe_category(
        name: str,
        default: RecipeCategory = RecipeCategory.OTHER
) -> RecipeCategory:
    """
    Returns the RecipeCategory Enum based on the given Enum name.
    """
    return RecipeCategory.__members__.get(name, default)


def get_product_category(
        name: str,
        default: ProductCategory = ProductCategory.OTHER
) -> ProductCategory:
    """
    Returns the ProductCategory Enum based on the given Enum name.
    """
    return ProductCategory.__members__.get(name, default)
