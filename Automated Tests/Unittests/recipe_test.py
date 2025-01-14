
import unittest
from Core.ingredient import Ingredient, AmountDefinition, NetAmountDefinition
from Core.product import Product, NutritionData
from Core.enums import RecipeCategory
from Core.recipe import Recipe, RecipeNetMassData


class TestRecipe(unittest.TestCase):

    def setUp(self):
        self.recipe = Recipe(item_id=1, name="Pancakes", category=RecipeCategory.MAIN_COURSE)

        self.flour_product = Product(1, "Flour", nutrition_data=NutritionData(300, 1, 60, 10))
        self.milk_product = Product(2, "Milk", nutrition_data=NutritionData(150, 5, 10, 8))
        self.egg_product = Product(3, "Egg", nutrition_data=NutritionData(70, 5, 1, 6))

        self.ingredient1 = Ingredient(
            item_id=1,
            product=self.flour_product,
            amount=200.0,
            net_amount=200.0,
            amount_definition=AmountDefinition.GRAMS,
            net_amount_definition=NetAmountDefinition.EQUAL
        )

        self.ingredient2 = Ingredient(
            item_id=2,
            product=self.milk_product,
            amount=250.0,
            net_amount=250.0,
            amount_definition=AmountDefinition.GRAMS,
            net_amount_definition=NetAmountDefinition.EQUAL
        )

        self.recipe.add_ingredient(self.ingredient1)
        self.recipe.add_ingredient(self.ingredient2)

    def test_add_ingredient(self):
        ingredient3 = Ingredient(
            item_id=3,
            product=self.egg_product,
            amount=50.0,
            net_amount=50.0,
            amount_definition=AmountDefinition.GRAMS,
            net_amount_definition=NetAmountDefinition.EQUAL
        )
        self.recipe.add_ingredient(ingredient3)

        self.assertIn(ingredient3.item_id, self.recipe.ingredients)
        self.assertEqual(len(self.recipe.ingredients), 3)

    def test_remove_ingredient(self):
        success = self.recipe.remove_ingredient(1)

        self.assertTrue(success)
        self.assertNotIn(1, self.recipe.ingredients)
        self.assertEqual(len(self.recipe.ingredients), 1)

    def test_get_total_amount(self):
        total_amount = self.recipe.get_total_amount()
        self.assertEqual(total_amount, 450.0)

    def test_get_total_net_mass(self):
        total_net_mass = self.recipe.get_total_net_mass()
        self.assertEqual(total_net_mass, 450.0)

    def test_get_net_mass_ratio(self):
        self.recipe.net_mass_data = RecipeNetMassData(measured_value=500, reduction=50, adjust_for_evaporation=True)

        net_mass_ratio = self.recipe.get_net_mass_ratio()
        expected_ratio = 450 / (500 - 50)
        self.assertAlmostEqual(net_mass_ratio, expected_ratio)

    def test_get_total_nutrition_data(self):
        total_nutrition = self.recipe.get_total_nutrition_data()

        self.assertEqual(total_nutrition.calories, 975)
        self.assertEqual(total_nutrition.fat, 14.5)
        self.assertEqual(total_nutrition.carbs, 145)
        self.assertEqual(total_nutrition.protein, 40)

    def test_get_total_nutrition_data_per_100g(self):
        nutrition_per_100g = self.recipe.get_total_nutrition_data_per_100g()

        self.assertAlmostEqual(nutrition_per_100g.calories, 216.67, places=2)
        self.assertAlmostEqual(nutrition_per_100g.fat, 3.22, places=2)
        self.assertAlmostEqual(nutrition_per_100g.carbs, 32.22, places=2)
        self.assertAlmostEqual(nutrition_per_100g.protein, 8.89, places=2)

    def test_convert_to_csv(self):
        csv_str = self.recipe.convert_to_csv()

        expected_string = (r'1;Pancakes;MAIN_COURSE;2;{"measured_value": 0.0, "reduction": 0.0, "average_ratio": 0.0,'
                           r' "adjust_for_evaporation": false};{"description": "", "prep_time": 0.0, "cooking_time":'
                           r' 0.0, "total_time": 0.0, "date_created": "2025-01-01"};'
                           r'{"1": "1|1|200.0|200.0|GRAMS|EQUAL|None", "2": "2|2|250.0|250.0|GRAMS|EQUAL|None"}')

        self.assertIn("Pancakes", csv_str)
        self.assertIn("MAIN_COURSE", csv_str)
        self.assertEqual(csv_str, expected_string)

    def test_convert_from_csv(self):
        csv_line = self.recipe.convert_to_csv()
        product_catalogue = {
            1: self.flour_product,
            2: self.milk_product,
            3: self.egg_product
        }

        restored_recipe = Recipe.convert_from_csv(csv_line, product_catalogue)

        self.assertEqual(restored_recipe.name, "Pancakes")
        self.assertEqual(len(restored_recipe.ingredients), 2)
        self.assertEqual(restored_recipe.get_total_amount(), 450.0)
