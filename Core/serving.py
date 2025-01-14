import copy
import json

from Core.consumable_abc import ConsumableItem
from Core.enums import ServingType, get_serving_type
from Core.product import NutritionData, Product
from Core.recipe import Recipe
from Core.savefile_functions import dataclass_to_dict, convert_to_float_at_index, dict_to_dataclass


class Serving:
    def __init__(
            self,
            item_id: int = 0,
            item_name: str = "",
            item_type: ServingType = ServingType.PRODUCT,
            portion: float = 0.0,
    ):
        """
        Serving object holding portion and nutrition data of a consumed Recipe or
        individual food Product item. Once created and added to the daily intake data record,
        the item nutrition data of the serving becomes independent and unaffected by
        any changes to either product catalogue or recipe definition.

        :param item_id:
        :param item_name:
        :param item_type:
        :param portion:
        """
        self.item_id = item_id
        self.item_name = item_name
        self.item_type = item_type
        self.portion = portion

        self.nutrition_data = NutritionData()

    @property
    def identifier_string(self) -> str:
        return f"{self.item_id}. {self.item_name}"

    def convert_to_csv(self, serving_delimiter: str = "|") -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        csv_data = [self.item_id,
                    self.item_name,
                    self.item_type.name,
                    self.portion,
                    json.dumps(dataclass_to_dict(self.nutrition_data))]

        csv_str = serving_delimiter.join([str(n) for n in csv_data])

        return csv_str

    @classmethod
    def convert_from_csv(cls, csv_line: str, delimiter: str = "|"):
        """
        Returns the object from a CSV line.
        """
        split_line = csv_line.split(delimiter)

        item_id = int(split_line[0])
        item_name = split_line[1]
        item_type = get_serving_type(split_line[2])
        portion = convert_to_float_at_index(split_line, index=3, default_value=0.0)
        nutrition_data_dict = json.loads(split_line[4])

        serving = cls(item_id, item_name, item_type, portion)
        serving.nutrition_data = dict_to_dataclass(NutritionData, nutrition_data_dict)

        return serving

    def update_item(self, item: ConsumableItem, new_item_id: int, new_item_name: str,
                    new_item_type: ServingType) -> None:
        """
        Updates the serving's item and recalculates the nutrition data.

        :param new_item_id: The ID of the new item.
        :param new_item_name: The name of the new item.
        :param new_item_type: The type of the new item (Recipe or Product).
        :param item: ConsumableItem object.
        """
        self.item_id = new_item_id
        self.item_name = new_item_name
        self.item_type = new_item_type

        if isinstance(item, Product):
            data = item.nutrition_data
        elif isinstance(item, Recipe):
            data = item.get_total_nutrition_data_per_100g()
        else:
            print(f"Error: Incompatible item {item} for {Serving}")
            data = NutritionData()

        self.nutrition_data = copy.copy(data)

    def set_nutrition_data(self, item: ConsumableItem):
        if isinstance(item, Product):
            data = item.nutrition_data
        elif isinstance(item, Recipe):
            data = item.get_total_nutrition_data_per_100g()
        else:
            print(f"Error: Incompatible item {item} for {Serving}")
            data = NutritionData()

        self.nutrition_data = copy.copy(data)

    def get_consumed_nutrition_values(self) -> NutritionData:
        return self.nutrition_data * (self.portion / 100)
