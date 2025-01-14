import unittest
from PySide6.QtCore import QDate, Qt
from Core.daily_intake import DailyIntake
from Core.serving import Serving
from Core.enums import ProductCategory, RecipeCategory
from Core.product import Product
from Core.ctr_data import CTRData


class TestCTRData(unittest.TestCase):

    def setUp(self):
        self.ctr_data = CTRData()

    def test_add_daily_intake(self):
        date_str = "2024-02-01"
        self.ctr_data.add_daily_intake(date_str)
        self.assertIn(date_str, self.ctr_data.daily_intake_record)
        self.assertIsInstance(self.ctr_data.daily_intake_record[date_str], DailyIntake)

    def test_remove_daily_intake(self):
        date_str = "2024-02-01"
        self.ctr_data.add_daily_intake(date_str)
        result = self.ctr_data.remove_daily_intake(date_str)
        self.assertTrue(result)
        self.assertNotIn(date_str, self.ctr_data.daily_intake_record)

    def test_duplicate_daily_intake(self):
        original_date = "2024-02-01"
        duplicate_date = "2024-02-02"
        self.ctr_data.add_daily_intake(original_date)
        self.ctr_data.duplicate_daily_intake(original_date, duplicate_date)

        self.assertIn(duplicate_date, self.ctr_data.daily_intake_record)
        self.assertEqual(
            self.ctr_data.daily_intake_record[duplicate_date].date,
            duplicate_date
        )

    def test_toggle_favorite_product(self):
        product = Product(1, "Test Product", category=ProductCategory.OTHER)
        self.ctr_data.product_catalogue[1] = product
        serving = Serving(1, "Serving of Test Product")

        self.assertFalse(self.ctr_data.serving_in_favorites(serving))
        self.ctr_data.toggle_favorite_serving(serving)
        self.assertTrue(self.ctr_data.serving_in_favorites(serving))
        self.ctr_data.toggle_favorite_serving(serving)
        self.assertFalse(self.ctr_data.serving_in_favorites(serving))

    def test_add_product(self):
        product = self.ctr_data.add_product("Apple", ProductCategory.FRUIT)
        self.assertIn(product.item_id, self.ctr_data.product_catalogue)
        self.assertEqual(product.name, "Apple")

    def test_remove_product(self):
        product = self.ctr_data.add_product("Banana")
        result = self.ctr_data.remove_product(product.item_id)
        self.assertTrue(result)
        self.assertNotIn(product.item_id, self.ctr_data.product_catalogue)

    def test_add_recipe(self):
        ctr_data = CTRData("Test Savefile")
        recipe = ctr_data.add_recipe("Pasta", RecipeCategory.MAIN_COURSE)
        self.assertIn(recipe.item_id, ctr_data.recipes_record)
        self.assertEqual(recipe.name, "Pasta")

    def test_remove_recipe(self):
        ctr_data = CTRData("Test Savefile")
        recipe = ctr_data.add_recipe("Pizza")
        result = ctr_data.remove_recipe(recipe.item_id)
        self.assertTrue(result)
        self.assertNotIn(recipe.item_id, ctr_data.recipes_record)

    def test_duplicate_product(self):
        ctr_data = CTRData("Test Savefile")

        original = ctr_data.add_product("Milk")
        duplicate = ctr_data.duplicate_product(original.item_id)

        self.assertIsNotNone(duplicate)
        self.assertNotEqual(original.item_id, duplicate.item_id)
        self.assertEqual(original.name, duplicate.name)

    def test_duplicate_recipe(self):
        ctr_data = CTRData("Test Savefile")

        original = ctr_data.add_recipe("Soup")
        duplicate = ctr_data.duplicate_recipe(original.item_id)

        self.assertIsNotNone(duplicate)
        self.assertNotEqual(original.item_id, duplicate.item_id)
        self.assertEqual(original.name, duplicate.name)

    def test_renumber_products(self):
        self.ctr_data.add_product("Carrot")
        self.ctr_data.add_product("Tomato")
        self.ctr_data.renumber_products()

        self.assertEqual(self.ctr_data.product_catalogue[1].name, "Carrot")
        self.assertEqual(self.ctr_data.product_catalogue[2].name, "Tomato")

    def test_renumber_recipes(self):
        ctr_data = CTRData("Test Savefile")

        ctr_data.add_recipe("Salad")
        ctr_data.add_recipe("Stew")
        ctr_data.renumber_recipes()

        self.assertEqual(ctr_data.recipes_record[1].name, "Salad")
        self.assertEqual(ctr_data.recipes_record[2].name, "Stew")

    def test_set_product_id(self):
        self.ctr_data.add_product("Juice")
        p2 = self.ctr_data.add_product("Water")

        self.ctr_data.set_product_id(p2, new_id=1)
        self.assertEqual(self.ctr_data.product_catalogue[1].name, "Water")
        self.assertEqual(self.ctr_data.product_catalogue[2].name, "Juice")

    def test_set_recipe_id(self):
        ctr_data = CTRData()

        ctr_data.add_recipe("Curry")
        r2 = ctr_data.add_recipe("Rice")

        ctr_data.set_recipe_id(r2, new_id=1)
        self.assertEqual(ctr_data.recipes_record[1].name, "Rice")
        self.assertEqual(ctr_data.recipes_record[2].name, "Curry")

    def test_duplicate_todays_daily_intake(self):
        today = QDate.currentDate().toString(Qt.DateFormat.ISODate)
        new_date = "2024-02-10"

        self.ctr_data.add_daily_intake(today)
        self.ctr_data.duplicate_todays_daily_intake(new_date)

        self.assertIn(new_date, self.ctr_data.daily_intake_record)
        self.assertEqual(self.ctr_data.daily_intake_record[new_date].date, new_date)

    def test_clear_data(self):
        ctr_data = CTRData()

        ctr_data.add_product("Bread")
        ctr_data.add_recipe("Omelette")
        ctr_data.add_daily_intake("2024-02-01")

        ctr_data.clear_catalogue_data()
        ctr_data.clear_recipe_data()
        ctr_data.clear_daily_intake_data()

        self.assertEqual(len(ctr_data.product_catalogue), 1)
        self.assertEqual(len(ctr_data.recipes_record), 1)
        self.assertEqual(len(ctr_data.daily_intake_record), 0)
