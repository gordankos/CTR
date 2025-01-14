from PySide6.QtCore import QDate

from Core.daily_intake import DailyIntake
from Core.savefile_functions import dataclass_to_dict
from Core.serving import Serving
from Core.enums import ProductCategory, RecipeCategory, ServingType
from Core.recipe import Recipe
from Core.product import Product, NutritionData

import json
import copy
from enum import Enum
from PySide6.QtCore import Qt


class SavefileExtension(Enum):
    CTR_DATA = ".ct"
    INFORMATION = ".cti"
    CATALOGUE = ".ctc"
    RECIPES = ".ctr"
    DAILY_INTAKE = ".ctd"


class CTRData:
    def __init__(
            self,
            filename: str = "CTR Savefile"
    ):
        """
        CTR data, containing all data used by the program,
        including a database of daily calorie intake, catalogue and all recipes.
        """
        self.filename = filename
        self.filepath: str = ""

        self.daily_intake_record: dict[str, DailyIntake] = {}
        self.product_catalogue: dict[int, Product] = {}
        self.recipes_record: dict[int, Recipe] = {}

        self.favorite_products: set[int] = set()
        self.favorite_recipes: set[int] = set()
        self.nutrition_targets = NutritionData()

        self.add_null_catalogue_entry()
        self.add_null_recipe_entry()

    def convert_to_csv(self) -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        csv_data = [self.filename,
                    self.filepath,
                    json.dumps(list(self.favorite_products)),
                    json.dumps(list(self.favorite_recipes)),
                    json.dumps(dataclass_to_dict(self.nutrition_targets))]

        csv_str = "\n".join([str(n) for n in csv_data])

        return csv_str

    def add_null_catalogue_entry(self) -> None:
        """
        Adds a default null entry as the first Product in the catalogue data.
        Enables selection of a null Product item in the daily intake table,
        as an alternative to deleting the table row.
        """
        self.product_catalogue[0] = Product(item_id=0, name="")

    def add_null_recipe_entry(self) -> None:
        """
        Adds a default null entry as the first Recipe in the recipe data.
        Enables selection of a null recipe in the daily intake table,
        as an alternative to deleting the table row.
        """
        self.recipes_record[0] = Recipe(item_id=0, name="")

    def add_daily_intake(self, date: str) -> DailyIntake:
        new_daily_intake = DailyIntake(date)
        self.daily_intake_record[date] = new_daily_intake
        return new_daily_intake

    def duplicate_daily_intake(self, date_string: str, override_date_string: str) -> None:
        """
        Copies daily intake data of the given date string and assigns it to the override date string.

        :param date_string: Date of the Daily intake record being duplicated.
        :param override_date_string: Date of the Daily intake record being overridden.
        """
        if date_string not in self.daily_intake_record.keys():
            print(f"Error: Daily intake record for date {date_string} does not exist!")
            return

        if override_date_string not in self.daily_intake_record.keys():
            self.add_daily_intake(override_date_string)

        intake_record = copy.deepcopy(self.daily_intake_record[date_string])
        intake_record.date = override_date_string

        self.daily_intake_record[override_date_string] = intake_record

    def duplicate_todays_daily_intake(self, date_string: str) -> None:
        """
        Duplicates todays' daily intake record for the next calendar day.
        """
        if date_string in self.daily_intake_record.keys():
            print(f"Error: Daily intake record for date {date_string} already exists!")
            return

        current_date: QDate = QDate.currentDate()
        current_date_string = current_date.toString(Qt.DateFormat.ISODate)

        if current_date_string not in self.daily_intake_record.keys():
            print(f"Daily intake record for todays' date {current_date_string} not found in CTR data! "
                  f"Adding a blank daily intake record for {date_string}.")
            self.add_daily_intake(date_string)
            return

        intake_record = copy.deepcopy(self.daily_intake_record[current_date_string])
        intake_record.date = date_string

        self.daily_intake_record[date_string] = intake_record

    def add_product(
            self,
            name: str,
            category: ProductCategory = ProductCategory.OTHER,
    ) -> Product:

        if self.product_catalogue:
            new_id = sorted(self.product_catalogue.keys())[-1] + 1
        else:
            new_id = 1

        new_product = Product(
            item_id=new_id,
            name=name,
            category=category)

        self.product_catalogue[new_product.item_id] = new_product
        return new_product

    def add_recipe(
            self,
            name: str,
            category: RecipeCategory = RecipeCategory.OTHER,
            description: str = ""
    ) -> Recipe:

        if self.recipes_record:
            new_id = sorted(self.recipes_record.keys())[-1] + 1
        else:
            new_id = 1

        new_recipe = Recipe(
            item_id=new_id,
            name=name,
            category=category)
        new_recipe.additional_data.description = description

        self.recipes_record[new_recipe.item_id] = new_recipe
        return new_recipe

    def toggle_favorite_serving(self, serving: Serving) -> bool:
        """
        Toggles the serving from the favorite products or recipes list depending on serving type.
        """
        favorites = (
            self.favorite_products if serving.item_type is ServingType.PRODUCT
            else self.favorite_recipes
        )

        if serving.item_id in favorites:
            favorites.remove(serving.item_id)
            return False
        else:
            favorites.add(serving.item_id)
            return True

    def serving_in_favorites(self, serving: Serving) -> bool:
        """
        Checks if the given serving is in favorite products or recipes list depending on serving type.
        """
        favorites = (
            self.favorite_products if serving.item_type is ServingType.PRODUCT
            else self.favorite_recipes
        )
        return serving.item_id in favorites

    def duplicate_product(self, product_id: int) -> Product | None:
        """
        Method generates a duplicate of the Product at the given ID and assigns it a new ID
        so it is below the original, while shifting all Product IDs below the duplicated item.
        """
        product = self.product_catalogue.get(product_id, None)
        if product is None:
            print(f"Error, Product ID {product_id} not found in the product catalogue for duplicate operation!")
            return None

        new_product = copy.deepcopy(product)
        new_product.item_id += 1

        keys_to_shift = sorted([key for key in self.product_catalogue if key > product_id], reverse=True)
        for key in keys_to_shift:
            self.product_catalogue[key + 1] = self.product_catalogue[key]
            self.product_catalogue[key + 1].item_id = key + 1

        self.product_catalogue[new_product.item_id] = new_product
        return new_product

    def duplicate_recipe(self, recipe_id: int) -> Recipe | None:
        recipe = self.recipes_record.get(recipe_id, None)
        if recipe is None:
            print(f"Error, Recipe ID {recipe_id} not found in the recipes dictionary for duplicate operation!")
            return None

        new_recipe = copy.deepcopy(recipe)
        new_id = sorted(self.recipes_record.keys())[-1] + 1
        new_recipe.item_id = new_id
        self.recipes_record[new_id] = new_recipe

        return new_recipe

    def renumber_products(self) -> None:
        """
        Renumbers all Products in the product catalogue dictionary starting with ID=1.
        """
        renumbered_dict: dict[int, Product] = {}
        for new_id, product in enumerate(self.product_catalogue.values(), start=0):
            product.item_id = new_id
            renumbered_dict[new_id] = product
        self.product_catalogue = renumbered_dict

    def renumber_recipes(self) -> None:
        """
        Renumbers all Recipes in the recipes dictionary starting with ID=1.
        """
        renumbered_dict: dict[int, Recipe] = {}
        for new_id, recipe in enumerate(self.recipes_record.values(), start=0):
            recipe.item_id = new_id
            renumbered_dict[new_id] = recipe
        self.recipes_record = renumbered_dict

    def renumber_product_ids(self, id_order: list[int]) -> None:
        """
        Renumbers Product catalogue dictionary based on the given order of IDs.
        :param id_order: List of existing IDs, to be renumbered in ascending order starting from ID=1.
        """
        renumbered_dict: dict[int, Product] = {}
        for new_id, item_id in enumerate(id_order, start=1):
            product = self.product_catalogue[item_id]
            product.item_id = new_id
            renumbered_dict[new_id] = product
        self.product_catalogue = renumbered_dict

    def renumber_recipe_ids(self, id_order: list[int]) -> None:
        """
        Renumbers Recipes dictionary based on the given order of IDs.
        :param id_order: List of existing IDs, to be renumbered in ascending order starting from ID=1.
        """
        renumbered_dict: dict[int, Recipe] = {}
        for new_id, item_id in enumerate(id_order, start=1):
            recipe = self.recipes_record[item_id]
            recipe.item_id = new_id
            renumbered_dict[new_id] = recipe
        self.recipes_record = renumbered_dict

    def set_product_id(self, product: Product, new_id: int) -> None:
        """
        Method sets the given ID for the Product and shifts the ID of all products in
        the products catalogue dictionary with ID greater than the new ID.
        """
        sorted_product_ids: list[int] = sorted([product.item_id for product in self.product_catalogue.values()])

        if new_id not in sorted_product_ids:
            print(f"New Product ID {new_id} not found in the products catalogue!")
            return

        if not (1 <= new_id <= len(self.product_catalogue)):
            print(f"Invalid new ID {new_id}. Input is restricted to between 1 and {len(self.product_catalogue)}.")
            return

        original_index = sorted_product_ids.index(product.item_id)
        sorted_product_ids.pop(original_index)

        if new_id >= len(self.product_catalogue):
            sorted_product_ids.append(product.item_id)
        else:
            indices = [index for index, product_id in enumerate(sorted_product_ids) if product_id > new_id]
            if indices:
                first_smallest_index = indices[0]
                insertion_index = first_smallest_index - 1 if new_id < product.item_id else first_smallest_index
            else:
                insertion_index = len(self.product_catalogue) - 2
            sorted_product_ids.insert(insertion_index, product.item_id)

        sorted_products: dict[int, Product] = {}

        for index, product_id in enumerate(sorted_product_ids, start=0):
            product = self.product_catalogue[product_id]
            product.item_id = index
            sorted_products[index] = product

        self.product_catalogue = sorted_products

    def set_recipe_id(self, recipe: Recipe, new_id: int):
        """
        Method sets the given ID for the Recipe and shifts the ID of all recipes in
        the recipes record dictionary with ID greater than the new ID.
        """
        if not (1 <= new_id <= len(self.recipes_record) - 1):
            print(f"Invalid new ID {new_id}. Input is restricted to between 1 and {len(self.recipes_record) - 1}.")
            return

        sorted_recipe_ids: list[int] = sorted([recipe.item_id
                                               for recipe in self.recipes_record.values()
                                               if recipe.item_id > 0])

        if new_id not in sorted_recipe_ids:
            print(f"New Recipe ID {new_id} not found in the recipes record!")
            return

        sorted_recipe_ids.remove(recipe.item_id)
        sorted_recipe_ids.insert(new_id - 1, recipe.item_id)

        sorted_recipes = {0: self.recipes_record[0]}
        for index, recipe_id in enumerate(sorted_recipe_ids, start=1):
            self.recipes_record[recipe_id].item_id = index
            sorted_recipes[index] = self.recipes_record[recipe_id]

        self.recipes_record = sorted_recipes

    def remove_daily_intake(self, date_string: str) -> bool:
        if date_string not in self.daily_intake_record.keys():
            print(f"Daily intake record for date {date_string} not found in CTR data!")
            return False

        self.daily_intake_record.pop(date_string)
        return True

    def remove_product(self, product_id: int) -> bool:
        if product_id not in self.product_catalogue.keys():
            print(f"Product ID {product_id} not found in CTR data!")
            return False

        self.product_catalogue.pop(product_id)
        return True

    def remove_recipe(self, recipe_id: int) -> bool:
        if recipe_id not in self.recipes_record.keys():
            print(f"Recipe ID {recipe_id} not found in CTR data!")
            return False

        self.recipes_record.pop(recipe_id)
        return True

    def get_all_product_names(self) -> list[str]:
        return [item.name for item in self.product_catalogue.values()]

    def get_all_recipe_names(self) -> list[str]:
        return [item.name for item in self.recipes_record.values()]

    def merge_catalogue_data(self, catalogue: dict[int, Product]) -> None:
        raise NotImplementedError

    def merge_recipe_data(self, recipes: dict[int, Recipe]) -> None:
        raise NotImplementedError

    def clear_daily_intake_data(self) -> None:
        self.daily_intake_record.clear()

    def clear_catalogue_data(self) -> None:
        self.product_catalogue.clear()
        self.add_null_catalogue_entry()

    def clear_recipe_data(self) -> None:
        self.recipes_record.clear()
        self.add_null_recipe_entry()
