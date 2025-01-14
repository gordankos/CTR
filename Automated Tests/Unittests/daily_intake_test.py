import unittest
from Core.serving import Serving
from Core.product import NutritionData
from Core.enums import ServingType
from Core.daily_intake import DailyIntake


class TestDailyIntake(unittest.TestCase):

    def setUp(self):
        self.daily_intake = DailyIntake("2025-02-07")

        self.serving_product = Serving(item_id=1, item_name="Apple", item_type=ServingType.PRODUCT, portion=150)
        self.serving_recipe = Serving(item_id=2, item_name="Smoothie", item_type=ServingType.RECIPE, portion=200)

        self.serving_product.nutrition_data = NutritionData(calories=52, protein=0.3, carbs=14, fat=0.2)
        self.serving_recipe.nutrition_data = NutritionData(calories=90, protein=2, carbs=18, fat=1)

    def test_initialization(self):
        self.assertEqual(self.daily_intake.date, "2025-02-07")
        self.assertFalse(self.daily_intake.has_data)
        self.assertEqual(len(self.daily_intake.consumed_products), 0)
        self.assertEqual(len(self.daily_intake.consumed_recipes), 0)

    def test_add_consumed_product(self):
        self.daily_intake.add_consumed_product(self.serving_product)
        self.assertTrue(self.daily_intake.has_data)
        self.assertEqual(len(self.daily_intake.consumed_products), 1)
        self.assertEqual(self.daily_intake.consumed_products[0].item_name, "Apple")

    def test_add_consumed_recipe(self):
        self.daily_intake.add_consumed_recipe(self.serving_recipe)
        self.assertTrue(self.daily_intake.has_data)
        self.assertEqual(len(self.daily_intake.consumed_recipes), 1)
        self.assertEqual(self.daily_intake.consumed_recipes[0].item_name, "Smoothie")

    def test_get_total_consumed_nutrition_data(self):
        self.daily_intake.add_consumed_product(self.serving_product)
        self.daily_intake.add_consumed_recipe(self.serving_recipe)

        total_nutrition = self.daily_intake.get_total_consumed_nutrition_data()

        expected_calories = (52 * 1.5) + (90 * 2)
        expected_protein = (0.3 * 1.5) + (2 * 2)
        expected_carbs = (14 * 1.5) + (18 * 2)
        expected_fat = (0.2 * 1.5) + (1 * 2)

        self.assertAlmostEqual(total_nutrition.calories, expected_calories, places=2)
        self.assertAlmostEqual(total_nutrition.protein, expected_protein, places=2)
        self.assertAlmostEqual(total_nutrition.carbs, expected_carbs, places=2)
        self.assertAlmostEqual(total_nutrition.fat, expected_fat, places=2)

    def test_convert_to_csv(self):
        self.daily_intake.add_consumed_product(self.serving_product)
        self.daily_intake.add_consumed_recipe(self.serving_recipe)

        csv_data = self.daily_intake.convert_to_csv()
        split_data = csv_data.split(";")

        self.assertEqual(split_data[0], "2025-02-07")
        self.assertTrue("Apple" in split_data[1])
        self.assertTrue("Smoothie" in split_data[2])

    def test_convert_from_csv(self):
        self.daily_intake.add_consumed_product(self.serving_product)
        self.daily_intake.add_consumed_recipe(self.serving_recipe)

        csv_data = self.daily_intake.convert_to_csv()
        restored_intake = DailyIntake.convert_from_csv(csv_data)

        self.assertEqual(restored_intake.date, "2025-02-07")
        self.assertEqual(len(restored_intake.consumed_products), 1)
        self.assertEqual(len(restored_intake.consumed_recipes), 1)
        self.assertEqual(restored_intake.consumed_products[0].item_name, "Apple")
        self.assertEqual(restored_intake.consumed_recipes[0].item_name, "Smoothie")
