
from Core.consumable_abc import ConsumableItem
from Core.enums import ServingType, ProductCategory, get_product_category
from Core.units import MeasurementUnit
from Core.savefile_functions import dataclass_to_dict, dict_to_dataclass

import json
from dataclasses import dataclass


@dataclass
class AdditionalData:
    """
    Represents additional information about a product, including its description,
    manufacturer, packaging details, and pricing.

    Attributes:
        description (str): Description of the product.
        store (str): Name of the store where the product was purchased with associated price.
        manufacturer (str): Name of the product's manufacturer.
        packaging_amount (float): Amount of product in the package.
        packaging_unit (MeasurementUnit): Measurement unit for the packaging amount.
        density (float): Density of the product in kilograms per liter.
        price (float): Price of the product.
        last_update_date (str): Date when the product details were last updated, "YYYY-MM-DD".
    """
    description: str = ""
    store: str = ""
    manufacturer: str = "",
    packaging_amount: float = 0.0
    packaging_unit: MeasurementUnit = MeasurementUnit.KG
    density: float = 1.0
    price: float = 0.0
    last_update_date: str = "2025-01-01"

    def get_mass_in_grams(self, item_amount: float) -> float:
        """
        Returns the mass in grams for the given product amount.
        """
        if self.packaging_unit is MeasurementUnit.G:
            return item_amount
        elif self.packaging_unit is MeasurementUnit.KG:
            return item_amount * 1000
        elif self.packaging_unit is MeasurementUnit.L:
            return item_amount * self.density * 1000
        elif self.packaging_unit is MeasurementUnit.ML:
            return item_amount * self.density

    def get_price_per_gram(self) -> float:
        """
        Returns the price per gram of the product.
        """
        if self.packaging_unit is MeasurementUnit.G:
            mass = self.packaging_amount
        elif self.packaging_unit is MeasurementUnit.KG:
            mass = self.packaging_amount * 1000
        elif self.packaging_unit is MeasurementUnit.L:
            mass = self.packaging_amount * self.density * 1000
        elif self.packaging_unit is MeasurementUnit.ML:
            mass = self.packaging_amount * self.density
        else:
            print(f"Measurement unit {self.packaging_unit} not supported for unit conversions "
                  f"in price per gram calculation method!")
            mass = 0.0

        if mass == 0.0:
            return 0

        return self.price / mass

    def get_price_for_mass(self, item_mass: float):
        """
        Returns the price for the given mass of product in grams.
        """
        price_per_gram = self.get_price_per_gram()
        return price_per_gram * item_mass


@dataclass
class NutritionData:
    """
    Represents food item nutrition data.

    Attributes:
        calories (float): Total calories or calories per 100 g, kcal.
        fat (float): Total fat or fat per 100 g, grams.
        carbs (float): Total carbs or carbs per 100 g, grams.
        protein (float): Total protein or protein per 100 g, grams.
    """
    calories: float = 0.0
    fat: float = 0.0
    carbs: float = 0.0
    protein: float = 0.0

    def get_macro_calories(self) -> tuple:
        """
        Returns macro calories based on standard calorie count in a gram of fat, carbs and protein, kcal.
        """
        fat_cal = self.fat * 9
        carbs_cal = self.carbs * 4
        protein_cal = self.protein * 4
        return fat_cal, carbs_cal, protein_cal

    def __add__(self, other):
        if not isinstance(other, NutritionData):
            return NotImplementedError(f"Can not add type {other} to NutritionData!")
        return NutritionData(
            calories=self.calories + other.calories,
            fat=self.fat + other.fat,
            carbs=self.carbs + other.carbs,
            protein=self.protein + other.protein,
        )

    def __mul__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplementedError(f"Can not multiply NutritionData with type {scalar}!")
        return NutritionData(
            calories=self.calories * scalar,
            fat=self.fat * scalar,
            carbs=self.carbs * scalar,
            protein=self.protein * scalar,
        )

    def __truediv__(self, scalar):
        if not isinstance(scalar, (int, float)):
            return NotImplementedError(f"Can not divide NutritionData with type {scalar}!")
        if scalar == 0:
            raise ValueError("Cannot divide NutritionData values by zero.")
        return NutritionData(
            calories=self.calories / scalar,
            fat=self.fat / scalar,
            carbs=self.carbs / scalar,
            protein=self.protein / scalar,
        )


class Product(ConsumableItem):
    def __init__(
            self,
            item_id: int,
            name: str,
            category: ProductCategory = ProductCategory.OTHER,
            nutrition_data: NutritionData | None = None,
            additional_data: AdditionalData | None = None
    ):
        """
        Object holding individual food product data.

        :param item_id: Item ID, used for referencing the Product in Recipes and other data types.
        :param name: Product name, descriptive or published by the manufacturer.
        :param category: Product category Enum.
        :param nutrition_data: Nutrition data.
        :param additional_data: Additional (optional) data.
        """
        super().__init__(item_id, name)
        self.category = category
        self.nutrition_data = nutrition_data if nutrition_data is not None else NutritionData()
        self.additional_data = additional_data if additional_data is not None else AdditionalData()

    @property
    def item_type(self) -> ServingType:
        return ServingType.PRODUCT

    def convert_to_csv(self, delimiter: str = ";") -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        csv_data = [self.item_id,
                    self.name,
                    self.category.name,
                    json.dumps(dataclass_to_dict(self.nutrition_data)),
                    json.dumps(dataclass_to_dict(self.additional_data))]

        csv_str = delimiter.join([str(n) for n in csv_data])

        return csv_str

    @classmethod
    def convert_from_csv(cls, csv_line: str, delimiter: str = ";"):
        """
        Returns the object from a CSV line.
        """
        split_line = csv_line.split(delimiter)

        item_id = int(split_line[0])
        name = split_line[1]
        category = get_product_category(split_line[2])
        nutrition_data_dict = json.loads(split_line[3])
        additional_data_dict = json.loads(split_line[4])

        nutrition_data = dict_to_dataclass(NutritionData, nutrition_data_dict)
        additional_data = dict_to_dataclass(AdditionalData, additional_data_dict)

        return cls(item_id, name, category, nutrition_data, additional_data)
