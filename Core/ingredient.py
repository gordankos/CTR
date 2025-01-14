from enum import Enum

from Core.product import Product, NutritionData
from Core.savefile_functions import convert_to_float_at_index, convert_to_int_at_index


class AmountDefinition(Enum):
    GRAMS = "Mass, g"
    RELATIVE_TO_AMOUNT = "Relative to Another Amount, %"
    RELATIVE_TO_NET_MASS = "Relative to Another Net Mass, %"


class NetAmountDefinition(Enum):
    """
    Recipe amount definition as a constant value or relative value to another value.
    """
    GRAMS = "Mass, g"
    EQUAL = "Equal to Amount"
    RELATIVE_TO_AMOUNT = "Relative to Amount, %"


def get_amount_definition(
        name: str,
        default: AmountDefinition = AmountDefinition.GRAMS
) -> AmountDefinition | None:
    """
    Returns the AmountDefinition Enum based on the given Enum name.
    """
    return AmountDefinition.__members__.get(name, default)


def get_net_amount_definition(
        name: str,
        default: NetAmountDefinition = NetAmountDefinition.GRAMS
) -> NetAmountDefinition | None:
    """
    Returns the NetAmountDefinition Enum based on the given Enum name.
    """
    return NetAmountDefinition.__members__.get(name, default)


class Ingredient:
    def __init__(
            self,
            item_id: int,
            product: Product,
            amount: float = 0.0,
            net_amount: float = 0.0,
            amount_definition: AmountDefinition = AmountDefinition.GRAMS,
            net_amount_definition: NetAmountDefinition = NetAmountDefinition.EQUAL,
    ):
        """
        Recipe ingredient object encapsulating a Product item with additional data for recipe definition.

        Note: Object uses a specific delimiter for csv data, enabling recipe data write in a single csv line.
        """
        self.item_id = item_id
        self.product = product
        self.amount = amount
        self.net_amount = net_amount
        self.amount_definition = amount_definition
        self.net_amount_definition = net_amount_definition

        self.amount_relative_to_id: int | None = None
        self.amount_relative_to: Ingredient | None = None

    @property
    def identifier_string(self) -> str:
        return f"{self.item_id}. {self.product.name}"

    @property
    def relative_amount_ingredient_id(self) -> int | None:
        if self.amount_relative_to is None:
            return None
        else:
            return self.amount_relative_to.item_id

    @property
    def amount_definition_unit_string(self) -> str:
        if self.amount_definition is AmountDefinition.GRAMS:
            return "g"
        else:
            return "%"

    @property
    def net_amount_definition_unit_string(self) -> str:
        if self.net_amount_definition is NetAmountDefinition.RELATIVE_TO_AMOUNT:
            return "%"
        else:
            return "g"

    def convert_to_csv(self, ingredient_delimiter: str = "|") -> str:
        """
        Returns the string representation of the object data for saving into a CSV save file.
        """
        csv_data = [self.item_id,
                    self.product.item_id,
                    self.amount,
                    self.net_amount,
                    self.amount_definition.name,
                    self.net_amount_definition.name,
                    self.relative_amount_ingredient_id]

        csv_str = ingredient_delimiter.join([str(n) for n in csv_data])

        return csv_str

    @classmethod
    def convert_from_csv(cls, csv_line: str, product_catalogue: dict[int, Product],
                         ingredient_delimiter: str = "|"):
        """
        Returns the object from a CSV line.
        """
        split_line = csv_line.split(ingredient_delimiter)
        item_id = int(split_line[0])
        product_id = int(split_line[1])
        product = product_catalogue.get(product_id, None)
        if product is None:
            print(f"Error: Product ID {product_id} not found in the Product catalogue!")
            product = product_catalogue[0]

        amount = convert_to_float_at_index(split_line, index=2, default_value=0.0)
        net_amount = convert_to_float_at_index(split_line, index=3, default_value=0.0)
        amount_definition = get_amount_definition(split_line[4])
        net_amount_definition = get_net_amount_definition(split_line[5])
        relative_ingredient = convert_to_int_at_index(split_line, index=6, default_value=None)
        ingredient = cls(item_id, product, amount, net_amount, amount_definition, net_amount_definition)
        ingredient.amount_relative_to_id = relative_ingredient

        return ingredient

    def detect_circular_reference(self, visited: set[int] | None = None):
        """
        Detects if there is a circular reference in the relative amount ingredient references.

        :param visited: Set of ingredient IDs already visited in the traversal.
        :return: True if a circular reference is detected, False otherwise.
        """
        if visited is None:
            visited = set()

        if self.item_id in visited:
            return True

        visited.add(self.item_id)

        if self.amount_relative_to is not None and self.amount_relative_to.detect_circular_reference(visited):
            return True

        visited.remove(self.item_id)
        return False

    def get_mass(self) -> float:
        """
        Returns the gross mass of the ingredient amount in grams (g).
        """
        if self.amount_definition is AmountDefinition.GRAMS:
            return self.amount

        elif self.amount_definition is AmountDefinition.RELATIVE_TO_AMOUNT:
            if self.amount_relative_to is not None:
                return (self.amount / 100) * self.amount_relative_to.amount
            else:
                return 0.0

        elif self.amount_definition is AmountDefinition.RELATIVE_TO_NET_MASS:
            if self.amount_relative_to is not None:
                return (self.amount / 100) * self.amount_relative_to.get_net_mass()
            else:
                return 0.0

        else:
            print(f"Error, Amount definition {self.amount_definition} "
                  f"is not a valid value for mass calculation!")
            return 0.0

    def get_net_mass(self) -> float:
        """
        Returns the gross mass of the ingredient amount in grams (g).
        """
        if self.net_amount_definition is NetAmountDefinition.GRAMS:
            return self.net_amount

        elif self.net_amount_definition is NetAmountDefinition.RELATIVE_TO_AMOUNT:
            return self.get_mass() * (self.net_amount / 100)

        elif self.net_amount_definition is NetAmountDefinition.EQUAL:
            return self.get_mass()

        else:
            print(f"Error, Net amount definition {self.net_amount_definition} "
                  f"is not a valid value for net mass calculation!")
            return 0.0

    def get_net_amount(self):
        if self.net_amount_definition in [NetAmountDefinition.GRAMS,
                                          NetAmountDefinition.RELATIVE_TO_AMOUNT]:
            return self.net_amount

        elif self.net_amount_definition is NetAmountDefinition.EQUAL:
            return self.get_mass()

        else:
            print(f"Error, Net amount definition {self.net_amount_definition} "
                  f"is not a valid value for net amount calculation!")
            return 0.0

    def get_nutrition_data(self) -> NutritionData:
        mass = self.get_net_mass()
        return self.product.nutrition_data * (mass / 100)

    def get_price(self) -> float:
        mass = self.get_mass()
        return self.product.additional_data.get_price_for_mass(mass)


