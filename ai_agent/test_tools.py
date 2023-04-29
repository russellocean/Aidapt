import os
import unittest

from tools import (
    calculate,
    create_file,
    delete_file,
    rename_file,
    search,
    view_file,
)

TEST_FILE_PATH = "test_file.txt"
RENAMED_TEST_FILE_PATH = "renamed_test_file.txt"


class TestTools(unittest.TestCase):
    def test_search(self):
        query = "Python programming"
        results = search(query)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_view_file(self):
        with open(TEST_FILE_PATH, "w") as file:
            file.write("This is a test file.")

        content = view_file(TEST_FILE_PATH)
        self.assertEqual(content, "This is a test file.")
        os.remove(TEST_FILE_PATH)

    def test_calculate(self):
        expression = "2 + 3 * 4"
        result = calculate(expression)
        self.assertEqual(result, "14")

    def test_create_file(self):
        content = "This is a test file."
        create_file(TEST_FILE_PATH, content)
        self.assertTrue(os.path.exists(TEST_FILE_PATH))
        os.remove(TEST_FILE_PATH)

    def test_delete_file(self):
        with open(TEST_FILE_PATH, "w") as file:
            file.write("This is a test file.")

        delete_file(TEST_FILE_PATH)
        self.assertFalse(os.path.exists(TEST_FILE_PATH))

    def test_rename_file(self):
        with open(TEST_FILE_PATH, "w") as file:
            file.write("This is a test file.")

        rename_file(TEST_FILE_PATH, RENAMED_TEST_FILE_PATH)
        self.assertTrue(os.path.exists(RENAMED_TEST_FILE_PATH))
        os.remove(RENAMED_TEST_FILE_PATH)

    # Add more test cases for other functions as needed


if __name__ == "__main__":
    unittest.main()
