

from Core.serving import Serving
from Core.product import NutritionData

import json


class DailyIntake:
    def __init__(
            self,
            date: str
    ):
        """
        Object holding daily calorie intake, separated into Recipes and
        individual food Product items for a particular calendar date.

        :param date: Date string in ISO format, such as '2024-12-31'
        """
        self.date = date

        self.consumed_products: list[Serving] = []
        self.consumed_recipes: list[Serving] = []

    @property
    def has_data(self) -> bool:
        """
        Returns True if daily intake record has consumed products or recipes added to respective lists.
        """
        if self.consumed_products or self.consumed_recipes:
            return True
        else:
            return False

    def convert_to_csv(self, delimiter: str = ";") -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        consumed_product_data = {index: serving.convert_to_csv()
                                 for index, serving in enumerate(self.consumed_products)}
        consumed_recipes_data = {index: serving.convert_to_csv()
                                 for index, serving in enumerate(self.consumed_recipes)}

        csv_data = [self.date,
                    json.dumps(consumed_product_data),
                    json.dumps(consumed_recipes_data)]

        csv_str = delimiter.join([str(n) for n in csv_data])

        return csv_str

    @classmethod
    def convert_from_csv(cls, csv_line: str, delimiter: str = ";"):
        """
        Returns the object from a CSV line.
        """
        split_line = csv_line.split(delimiter)

        date_string = split_line[0]
        consumed_products_dict: dict = json.loads(split_line[1])
        consumed_recipes_dict: dict = json.loads(split_line[2])

        daily_intake = cls(date_string)

        for product_data in consumed_products_dict.values():
            daily_intake.add_consumed_product(Serving.convert_from_csv(product_data))

        for recipe_data in consumed_recipes_dict.values():
            daily_intake.add_consumed_recipe(Serving.convert_from_csv(recipe_data))

        return daily_intake

    def add_consumed_product(self, serving: Serving) -> None:
        self.consumed_products.append(serving)

    def add_consumed_recipe(self, serving: Serving) -> None:
        self.consumed_recipes.append(serving)

    def get_total_consumed_nutrition_data(self) -> NutritionData:
        data = NutritionData()

        for serving in self.consumed_products:
            data += serving.get_consumed_nutrition_values()

        for serving in self.consumed_recipes:
            data += serving.get_consumed_nutrition_values()

        return data
