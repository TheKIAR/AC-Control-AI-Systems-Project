import json
import unittest
from src.data_driven.generator import DataGenerator

class TestDataGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = DataGenerator()

    def test_generate_supervised_data(self):
        data = self.generator.generate_supervised_data()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) > 0)

    def test_generate_unsupervised_data(self):
        data = self.generator.generate_unsupervised_data()
        self.assertIsNotNone(data)
        self.assertTrue(len(data) > 0)

    def test_data_cleaning(self):
        raw_data = [None, 1, 2, None, 3]
        cleaned_data = self.generator.clean_data(raw_data)
        self.assertEqual(cleaned_data, [1, 2, 3])

    def test_data_transformation(self):
        raw_data = [1, 2, 3]
        transformed_data = self.generator.transform_data(raw_data)
        self.assertEqual(transformed_data, [1, 4, 9])

    def test_save_and_load(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as directory:
            filename = f"{directory}/data.json"
            original = self.generator.generate_supervised_data(3)
            self.generator.save_data(original, filename)
            loaded = self.generator.load_data(filename)
            self.assertEqual(loaded, original)
            with open(filename, encoding="utf-8") as file:
                self.assertIsInstance(json.load(file), list)

if __name__ == '__main__':
    unittest.main()