
import unittest
from Core.product import Product, AdditionalData, NutritionData
from Core.enums import ProductCategory, ServingType
from Core.units import MeasurementUnit
from GUI.Common.gui_util_functions import strip_forbidden_characters


class TestProduct(unittest.TestCase):

    def setUp(self):
        self.nutrition = NutritionData(calories=100, fat=5, carbs=20, protein=3)
        self.additional = AdditionalData(
            description="Chicken",
            store="Healthy Foods",
            manufacturer="Mills",
            packaging_amount=500,
            packaging_unit=MeasurementUnit.G,
            price=5.99,
            last_update_date="2025-01-01"
        )
        self.product = Product(
            item_id=1,
            name="Chicken",
            category=ProductCategory.MEAT,
            nutrition_data=self.nutrition,
            additional_data=self.additional
        )

    def test_initialization(self):
        self.assertEqual(self.product.item_id, 1)
        self.assertEqual(self.product.name, "Chicken")
        self.assertEqual(self.product.category, ProductCategory.MEAT)
        self.assertEqual(self.product.nutrition_data.calories, 100)
        self.assertEqual(self.product.additional_data.description, "Chicken")

    def test_item_type(self):
        self.assertEqual(self.product.item_type, ServingType.PRODUCT)

    def test_convert_to_csv(self):
        csv_data = self.product.convert_to_csv()
        split_data = csv_data.split(";")

        self.assertEqual(int(split_data[0]), 1)
        self.assertEqual(split_data[1], "Chicken")
        self.assertEqual(split_data[2], "MEAT")
        self.assertTrue("calories" in split_data[3])
        self.assertTrue("description" in split_data[4])

    def test_convert_from_csv(self):
        csv_data = self.product.convert_to_csv()
        restored_product = Product.convert_from_csv(csv_data)

        self.assertEqual(restored_product.item_id, 1)
        self.assertEqual(restored_product.name, "Chicken")
        self.assertEqual(restored_product.category, ProductCategory.MEAT)
        self.assertEqual(restored_product.nutrition_data.calories, 100)
        self.assertEqual(restored_product.additional_data.description, "Chicken")

    def test_nutrition_data_operations(self):
        multiplied = self.nutrition * 2
        divided = self.nutrition / 2
        added = self.nutrition + NutritionData(calories=50, fat=2, carbs=10, protein=1)

        self.assertEqual(multiplied.calories, 200)
        self.assertEqual(divided.calories, 50)
        self.assertEqual(added.calories, 150)

    def test_additional_data_price_per_gram(self):
        price_per_gram = self.additional.get_price_per_gram()
        self.assertAlmostEqual(price_per_gram, 5.99 / 500, places=4)

    def test_additional_data_price_for_mass(self):
        price_for_250g = self.additional.get_price_for_mass(250)
        expected_price = (5.99 / 500) * 250
        self.assertAlmostEqual(price_for_250g, expected_price, places=4)

    def test_unit_conversion(self):
        data = AdditionalData(
            description="Milk",
            store="Dairy Farm",
            manufacturer="Fresh Dairy",
            packaging_amount=1,
            packaging_unit=MeasurementUnit.L,
            density=1.03,
            price=1.50,
            last_update_date="2025-01-01"
        )

        self.assertEqual(data.get_mass_in_grams(1), 1030)
        self.assertEqual(data.get_mass_in_grams(0.5), 515)


class TestProductEdgeCases(unittest.TestCase):

    def test_zero_and_negative_packaging_amount(self):
        zero_packaging = AdditionalData(packaging_amount=0, packaging_unit=MeasurementUnit.KG)
        negative_packaging = AdditionalData(packaging_amount=-1, packaging_unit=MeasurementUnit.KG)

        self.assertEqual(zero_packaging.get_mass_in_grams(1), 1000)
        self.assertEqual(negative_packaging.get_mass_in_grams(-1), -1000)

    def test_extreme_density_values(self):
        high_density = AdditionalData(packaging_amount=1, packaging_unit=MeasurementUnit.L, density=1.5)
        low_density = AdditionalData(packaging_amount=1, packaging_unit=MeasurementUnit.L, density=0.5)

        self.assertEqual(high_density.get_mass_in_grams(1), 1500)
        self.assertEqual(low_density.get_mass_in_grams(1), 500)

    def test_price_per_gram_calculation(self):
        free_product = AdditionalData(packaging_amount=1, packaging_unit=MeasurementUnit.KG, price=0)
        negative_price = AdditionalData(packaging_amount=1, packaging_unit=MeasurementUnit.KG, price=-5)

        self.assertEqual(free_product.get_price_per_gram(), 0)
        self.assertLess(negative_price.get_price_per_gram(), 0)

    def test_csv_conversion_sanitization(self):
        raw_name = 'Oat"meal | Del;uxe, New\nLine\tTest'
        expected_sanitized_name = 'Oatmeal  Deluxe, NewLineTest'

        product = Product(1, raw_name, ProductCategory.OTHER)

        sanitized_name_in_csv = strip_forbidden_characters(product.name)

        self.assertEqual(sanitized_name_in_csv, expected_sanitized_name)


if __name__ == "__main__":
    unittest.main()
