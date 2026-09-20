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
        self.assertEqual(transformed_data, [1, 4, 9])  # Example transformation: squaring the data

if __name__ == '__main__':
    unittest.main()