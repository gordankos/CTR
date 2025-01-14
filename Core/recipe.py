
from Core.consumable_abc import ConsumableItem
from Core.ingredient import Ingredient
from Core.product import Product, NutritionData
from Core.enums import ServingType, RecipeCategory, get_recipe_category
from Core.savefile_functions import (dataclass_to_dict, dict_to_dataclass)

import json
from dataclasses import dataclass


@dataclass
class RecipeNetMassData:
    """
    Holds net mass data and additional information related to
    water evaporation compensation calculations.

    Attributes:
        measured_value (float): Measured net mass of the dish, g.
        reduction (float): Reduction to the measured net mass, known pot / pan / container mass, g.
        average_ratio (float): Average total net mass to measured net mass ratio (before and after cooking).
        adjust_for_evaporation (bool): Use measured mass of the dish to account for water evaporation.
            If False, uses total net mass (sum of all recipe ingredients) for net nutrition value calculation.
    """
    measured_value: float = 0.0
    reduction: float = 0.0
    average_ratio: float = 0.0
    adjust_for_evaporation: bool = False


@dataclass
class AdditionalRecipeData:
    """
    Represents additional information about a recipe, including its description,
    preparation times, creation date, etc.

    Attributes:
        description (str): Description of the product.
        prep_time (str): Preparation time required to make the dish.
        cooking_time (str): Cooking time.
        total_time (str): Total time required to make the dish.
        date_created (str): Date when the recipe was created.
    """
    description: str = ""
    prep_time: float = 0.0
    cooking_time: float = 0.0
    total_time: float = 0.0
    date_created: str = "2025-01-01"


class Recipe(ConsumableItem):
    def __init__(
            self,
            item_id: int,
            name: str,
            category: RecipeCategory = RecipeCategory.OTHER,
            net_mass_data: RecipeNetMassData | None = None,
            additional_data: AdditionalRecipeData | None = None
    ):
        """
        Recipe object holding full recipe data.

        :param item_id:
        :param name:
        :param category:
        """
        super().__init__(item_id, name)
        self.category = category
        self.net_mass_data = net_mass_data if net_mass_data is not None else RecipeNetMassData()
        self.additional_data = additional_data if additional_data is not None else AdditionalRecipeData()

        self.ingredients: dict[int, Ingredient] = {}

    @property
    def item_type(self) -> ServingType:
        return ServingType.RECIPE

    def convert_to_csv(self, delimiter: str = ";") -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        recipe_data = {key: ingredient.convert_to_csv() for key, ingredient in self.ingredients.items()}

        csv_data = [self.item_id, self.name,
                    self.category.name,
                    len(self.ingredients),
                    json.dumps(dataclass_to_dict(self.net_mass_data)),
                    json.dumps(dataclass_to_dict(self.additional_data)),
                    json.dumps(recipe_data)]

        csv_str = delimiter.join([str(n) for n in csv_data])

        return csv_str

    @classmethod
    def convert_from_csv(cls, csv_line: str, product_catalogue: dict[int, Product], delimiter: str = ";"):
        """
        Returns the object from a CSV line.
        """
        split_line = csv_line.split(delimiter)

        recipe_id = int(split_line[0])
        name = split_line[1]
        category = get_recipe_category(split_line[2])
        ingredients_count = int(split_line[3])
        net_mass_data_dict = json.loads(split_line[4])
        additional_data_dict = json.loads(split_line[5])

        net_mass_data = dict_to_dataclass(RecipeNetMassData, net_mass_data_dict)
        additional_data = dict_to_dataclass(AdditionalRecipeData, additional_data_dict)

        recipe = cls(recipe_id, name, category, net_mass_data, additional_data)

        if ingredients_count > 0:
            ingredients_dict: dict = json.loads(split_line[6])
            for ingredient_csv_data in ingredients_dict.values():
                ingredient = Ingredient.convert_from_csv(product_catalogue=product_catalogue,
                                                         csv_line=ingredient_csv_data)
                recipe.ingredients[ingredient.item_id] = ingredient
            recipe.update_ingredient_references()

        return recipe

    def add_ingredient(self, ingredient: Ingredient):
        if self.ingredients:
            new_id = sorted(self.ingredients.keys())[-1] + 1
        else:
            new_id = 1

        ingredient.item_id = new_id

        self.ingredients[new_id] = ingredient
        return ingredient

    def remove_ingredient(self, ingredient_id: int) -> bool:
        """
        Removes the selected ingredient from the recipe ingredients dictionary.
        Checks for and removes any references to the ingredient as part of relative amount definition.
        """
        if ingredient_id not in self.ingredients.keys():
            print(f"Ingredient ID {ingredient_id} not found in recipe {self.identifier_string}!")
            return False

        selected_ingredient = self.ingredients[ingredient_id]

        for ingredient in self.ingredients.values():
            if ingredient.relative_amount_ingredient_id == selected_ingredient.item_id:
                print(f"Removing reference of {selected_ingredient.identifier_string} "
                      f"from {ingredient.identifier_string}...")
                ingredient.amount_relative_to = None

        self.ingredients.pop(ingredient_id)
        return True

    def renumber_ingredients(self):
        """
        Renumbers all Ingredients in the ingredients dictionary starting with ID=1.
        """
        renumbered_dict: dict[int, Ingredient] = {}
        for new_id, ingredient in enumerate(self.ingredients.values(), start=1):
            ingredient.item_id = new_id
            renumbered_dict[new_id] = ingredient
        self.ingredients = renumbered_dict

    def set_ingredient_id(self, ingredient: Ingredient, new_id: int):
        """
        Method sets the given ID for the Ingredient and renumbers all existing ingredients in the recipe.
        """
        sorted_ingredient_ids: list[int] = list(sorted([ingredient.item_id for ingredient in self.ingredients.values()]))

        if new_id not in sorted_ingredient_ids:
            print(f"New Ingredient ID {new_id} not found in the recipe ingredients!")
            return

        if not (1 <= new_id <= len(self.ingredients)):
            print(f"Invalid new ID {new_id}. Input is restricted to between 1 and {len(self.ingredients)}.")
            return

        original_index = sorted_ingredient_ids.index(ingredient.item_id)
        sorted_ingredient_ids.pop(original_index)

        if new_id >= len(self.ingredients):
            sorted_ingredient_ids.append(ingredient.item_id)
        else:
            indices = [index for index, ingredient_id in enumerate(sorted_ingredient_ids) if ingredient_id > new_id]
            if indices:
                first_smallest_index = indices[0]
                insertion_index = first_smallest_index - 1 if new_id < ingredient.item_id else first_smallest_index
            else:
                insertion_index = len(self.ingredients) - 2
            sorted_ingredient_ids.insert(insertion_index, ingredient.item_id)

        sorted_ingredients: dict[int, Ingredient] = {}
        for index, ingredient_id in enumerate(sorted_ingredient_ids, start=1):
            ingredient = self.ingredients[ingredient_id]
            ingredient.item_id = index
            sorted_ingredients[index] = ingredient

        self.ingredients = sorted_ingredients

    def update_ingredient_references(self):
        """
        Sets object references between ingredients based on relative ingredient IDs.
        """
        for ingredient in self.ingredients.values():
            if ingredient.amount_relative_to_id is None:
                continue

            rel_ingredient = self.ingredients.get(ingredient.amount_relative_to_id, None)
            if rel_ingredient is None:
                continue

            ingredient.amount_relative_to = rel_ingredient

    def get_ingredient(self, ingredient_id: int) -> Ingredient | None:
        return self.ingredients.get(ingredient_id, None)

    def get_total_amount(self) -> float:
        amount = 0.0
        for ingredient in self.ingredients.values():
            amount += ingredient.amount
        return amount

    def get_total_net_mass(self) -> float:
        net_amount = 0.0
        for ingredient in self.ingredients.values():
            net_amount += ingredient.get_net_mass()
        return net_amount

    def get_total_price(self) -> float:
        price = 0.0
        for ingredient in self.ingredients.values():
            price += ingredient.get_price()
        return price

    def get_net_measured_mass(self) -> float:
        return max([0.0, self.net_mass_data.measured_value - self.net_mass_data.reduction])

    def get_net_mass_ratio(self) -> float:
        total_net_mass = self.get_total_net_mass()
        if total_net_mass == 0.0:
            return 0.0

        if self.net_mass_data.adjust_for_evaporation:
            net_measured_mass = self.get_net_measured_mass()
            if net_measured_mass == 0.0:
                return 0.0
            return total_net_mass / net_measured_mass

        else:
            return 1

    def get_total_nutrition_data(self) -> NutritionData:
        data = NutritionData()
        for ingredient in self.ingredients.values():
            data += ingredient.get_nutrition_data()
        return data

    def get_price_per_100g(self) -> float:
        total_net_mass = self.get_total_net_mass()
        if total_net_mass == 0.0:
            return 0.0

        if self.net_mass_data.adjust_for_evaporation:
            net_measured_mass = self.get_net_measured_mass()
            if net_measured_mass == 0.0:
                return 0.0
            ratio = total_net_mass / net_measured_mass
        else:
            ratio = 1

        price_per_gram = self.get_total_price() / total_net_mass
        return price_per_gram * ratio * 100

    def get_total_nutrition_data_per_100g(self) -> NutritionData:
        total_net_mass = self.get_total_net_mass()
        if total_net_mass == 0.0:
            return NutritionData()

        net_measured_mass = self.get_net_measured_mass()
        total_nutrition = self.get_total_nutrition_data()
        data_per_gram = total_nutrition / total_net_mass

        if self.net_mass_data.adjust_for_evaporation:
            if net_measured_mass == 0.0:
                return NutritionData()
            ratio = total_net_mass / net_measured_mass
        else:
            ratio = 1.0

        return data_per_gram * ratio * 100
