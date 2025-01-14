import unittest
from Core.enums import ServingType
from Core.product import NutritionData, Product
from Core.serving import Serving


class TestServing(unittest.TestCase):

    def setUp(self):
        self.serving = Serving(item_id=1, item_name="Test Item", item_type=ServingType.PRODUCT, portion=150.0)

    def test_initialization(self):
        self.assertEqual(self.serving.item_id, 1)
        self.assertEqual(self.serving.item_name, "Test Item")
        self.assertEqual(self.serving.item_type, ServingType.PRODUCT)
        self.assertEqual(self.serving.portion, 150.0)
        self.assertIsInstance(self.serving.nutrition_data, NutritionData)

    def test_identifier_string(self):
        self.assertEqual(self.serving.identifier_string, "1. Test Item")

    def test_convert_to_csv(self):
        csv_data = self.serving.convert_to_csv()
        expected_prefix = "1|Test Item|PRODUCT|150.0|"
        self.assertTrue(csv_data.startswith(expected_prefix))

    def test_convert_from_csv(self):
        csv_line = '2|Rice|PRODUCT|100.0|{"calories": 200, "protein": 4.5}'
        serving = Serving.convert_from_csv(csv_line)

        self.assertEqual(serving.item_id, 2)
        self.assertEqual(serving.item_name, "Rice")
        self.assertEqual(serving.item_type, ServingType.PRODUCT)
        self.assertEqual(serving.portion, 100.0)
        self.assertEqual(serving.nutrition_data.calories, 200)
        self.assertEqual(serving.nutrition_data.protein, 4.5)

    def test_update_item(self):
        product = Product(2, "Updated Product", nutrition_data=NutritionData(calories=300, protein=10))
        self.serving.update_item(product, new_item_id=2, new_item_name="Updated Product",
                                 new_item_type=ServingType.PRODUCT)

        self.assertEqual(self.serving.item_id, 2)
        self.assertEqual(self.serving.item_name, "Updated Product")
        self.assertEqual(self.serving.nutrition_data.calories, 300)
        self.assertEqual(self.serving.nutrition_data.protein, 10)

    def test_get_consumed_nutrition_values(self):
        self.serving.nutrition_data = NutritionData(calories=200, protein=10)  # Per 100g
        consumed = self.serving.get_consumed_nutrition_values()

        self.assertEqual(consumed.calories, 200 * 1.5)  # 150g portion
        self.assertEqual(consumed.protein, 10 * 1.5)

    def test_set_nutrition_data_with_recipe(self):
        product = Product(3, "Test Product")
        product.nutrition_data = NutritionData(calories=400, protein=20)

        self.serving.set_nutrition_data(product)

        self.assertEqual(self.serving.nutrition_data.calories, 400)
        self.assertEqual(self.serving.nutrition_data.protein, 20)
