import unittest
import csv
from io import StringIO
from your_module import export_to_csv

class TestCSVExport(unittest.TestCase):
    def test_export_to_csv_format(self):
        data = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
        output = export_to_csv(data)
        self.assertIsInstance(output, str)
        self.assertTrue(output.startswith('name,age\n'))

    def test_export_to_csv_data_inclusion(self):
        data = [{'name': 'John', 'age': 30}, {'name': 'Jane', 'age': 25}]
        output = export_to_csv(data)
        expected_output = 'name,age\nJohn,30\nJane,25\n'
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()