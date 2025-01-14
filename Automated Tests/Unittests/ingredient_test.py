import unittest
from Core.product import Product, NutritionData
from Core.ingredient import (Ingredient, AmountDefinition, NetAmountDefinition,
                             get_amount_definition, get_net_amount_definition)


class TestIngredient(unittest.TestCase):

    def setUp(self):
        self.product1 = Product(
            item_id=1,
            name="Test Product",
            nutrition_data=NutritionData(10, 5, 3, 2))

        self.product2 = Product(
            item_id=2,
            name="Another Product",
            nutrition_data=NutritionData(20, 10, 6, 4))

        self.ingredient1 = Ingredient(
            item_id=1,
            product=self.product1,
            amount=100,
            net_amount=80,
            amount_definition=AmountDefinition.GRAMS,
            net_amount_definition=NetAmountDefinition.GRAMS
        )

        self.ingredient2 = Ingredient(
            item_id=2,
            product=self.product2,
            amount=50,
            net_amount=40,
            amount_definition=AmountDefinition.RELATIVE_TO_AMOUNT,
            net_amount_definition=NetAmountDefinition.RELATIVE_TO_AMOUNT
        )
        self.ingredient2.amount_relative_to = self.ingredient1

    def test_initialization(self):
        self.assertEqual(self.ingredient1.item_id, 1)
        self.assertEqual(self.ingredient1.product.name, "Test Product")
        self.assertEqual(self.ingredient1.amount, 100)
        self.assertEqual(self.ingredient1.net_amount, 80)
        self.assertEqual(self.ingredient1.amount_definition, AmountDefinition.GRAMS)

    def test_get_mass(self):
        self.assertEqual(self.ingredient1.get_mass(), 100)
        self.assertEqual(self.ingredient2.get_mass(), 50)

    def test_get_net_mass(self):
        self.assertEqual(self.ingredient1.get_net_mass(), 80)
        self.assertEqual(self.ingredient2.get_net_mass(), 20)

    def test_identifier_string(self):
        self.assertEqual(self.ingredient1.identifier_string, "1. Test Product")

    def test_amount_definition_unit_string(self):
        self.assertEqual(self.ingredient1.amount_definition_unit_string, "g")
        self.assertEqual(self.ingredient2.amount_definition_unit_string, "%")

    def test_net_amount_definition_unit_string(self):
        self.assertEqual(self.ingredient1.net_amount_definition_unit_string, "g")
        self.assertEqual(self.ingredient2.net_amount_definition_unit_string, "%")

    def test_convert_to_csv(self):
        csv_line = self.ingredient1.convert_to_csv()
        self.assertIn("1|1|100|80|GRAMS|GRAMS|None", csv_line)

    def test_convert_from_csv(self):
        csv_line = "2|2|50|40|RELATIVE_TO_AMOUNT|RELATIVE_TO_AMOUNT|1"
        product_catalogue = {1: self.product1, 2: self.product2}

        ingredient_from_csv = Ingredient.convert_from_csv(csv_line, product_catalogue)
        self.assertEqual(ingredient_from_csv.item_id, 2)
        self.assertEqual(ingredient_from_csv.product.name, "Another Product")
        self.assertEqual(ingredient_from_csv.amount, 50)
        self.assertEqual(ingredient_from_csv.net_amount, 40)
        self.assertEqual(ingredient_from_csv.amount_definition, AmountDefinition.RELATIVE_TO_AMOUNT)

    def test_detect_circular_reference(self):
        self.assertFalse(self.ingredient1.detect_circular_reference())

        self.ingredient1.amount_relative_to = self.ingredient2
        self.ingredient2.amount_relative_to = self.ingredient1

        self.assertTrue(self.ingredient1.detect_circular_reference())
        self.assertTrue(self.ingredient2.detect_circular_reference())

    def test_get_amount_definition(self):
        self.assertEqual(get_amount_definition(name="GRAMS"), AmountDefinition.GRAMS)
        self.assertEqual(get_amount_definition(name="INVALID", default=AmountDefinition.RELATIVE_TO_AMOUNT), AmountDefinition.RELATIVE_TO_AMOUNT)

    def test_get_net_amount_definition(self):
        self.assertEqual(get_net_amount_definition(name="EQUAL"), NetAmountDefinition.EQUAL)
        self.assertEqual(get_net_amount_definition(name="INVALID", default=NetAmountDefinition.GRAMS), NetAmountDefinition.GRAMS)


class TestIngredientMassCalculations(unittest.TestCase):

    def setUp(self):

        self.product = Product(
            item_id=1,
            name="Test Product",
            nutrition_data=NutritionData(10, 5, 3, 2))

        self.ref_product = Product(
            item_id=2,
            name="Another Product",
            nutrition_data=NutritionData(20, 10, 6, 4))

    def run_sub_test(
            self,
            index,
            amount_def: AmountDefinition,
            net_amount_def: NetAmountDefinition,
            amount: float,
            net_amount: float,
            ref_mass: float | None,
            ref_net_mass: float | None,
            expected_mass: float,
            expected_net_mass: float
    ) -> None:

        with self.subTest(f"Combination {index}; "
                          f"Amount: {amount_def.name}; "
                          f"Net Amount: {net_amount_def.name}"):

            ingredient = Ingredient(
                item_id=1,
                product=self.product,
                amount=amount,
                net_amount=net_amount,
                amount_definition=amount_def,
                net_amount_definition=net_amount_def)

            if ref_mass is not None and ref_net_mass is not None:
                reference_ingredient = Ingredient(
                    item_id=2,
                    product=self.ref_product,
                    amount=ref_mass,
                    net_amount=ref_net_mass,
                    amount_definition=AmountDefinition.GRAMS,
                    net_amount_definition=NetAmountDefinition.GRAMS)

                ingredient.amount_relative_to = reference_ingredient

            self.assertAlmostEqual(ingredient.get_mass(), expected_mass,
                                   msg=f"Failed mass check for {amount_def.name}, {net_amount_def.name}")
            self.assertAlmostEqual(ingredient.get_net_mass(), expected_net_mass,
                                   msg=f"Failed net mass check for {amount_def.name}, {net_amount_def.name}")

    def test_all_combinations(self):
        """
        Test cases for all combinations of amount and net amount definition.

        See Validation Docs/Validation Test Cases.xlsx for calculated values.
        """
        test_cases: list[tuple] = [
            (AmountDefinition.GRAMS, NetAmountDefinition.GRAMS, 100, 80, None, None, 100, 80),
            (AmountDefinition.GRAMS, NetAmountDefinition.EQUAL, 100, 0, None, None, 100, 100),
            (AmountDefinition.GRAMS, NetAmountDefinition.RELATIVE_TO_AMOUNT, 100, 50, None, None, 100, 50),
            (AmountDefinition.RELATIVE_TO_AMOUNT, NetAmountDefinition.GRAMS, 50, 80, 200, 150, 100, 80),
            (AmountDefinition.RELATIVE_TO_AMOUNT, NetAmountDefinition.EQUAL, 50, 0, 200, 150, 100, 100),
            (AmountDefinition.RELATIVE_TO_AMOUNT, NetAmountDefinition.RELATIVE_TO_AMOUNT, 50, 50, 200, 150, 100, 50),
            (AmountDefinition.RELATIVE_TO_NET_MASS, NetAmountDefinition.GRAMS, 50, 80, 200, 150, 75, 80),
            (AmountDefinition.RELATIVE_TO_NET_MASS, NetAmountDefinition.EQUAL, 50, 0, 200, 150, 75, 75),
            (AmountDefinition.RELATIVE_TO_NET_MASS, NetAmountDefinition.RELATIVE_TO_AMOUNT, 50, 50, 200, 150, 75, 37.5),
        ]

        for i, test_tuple in enumerate(test_cases, 1):
            self.run_sub_test(i, *test_tuple)
