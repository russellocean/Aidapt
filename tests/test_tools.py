import unittest

from rich import print as rprint
from rich.table import Table
from rich.traceback import install

from agents.tools import (
    calculate,
    create_file,
    delete_file,
    rename_file,
    search,
    view_file,
)
from database.memory_database import MemoryDatabase

install()  # Enables rich's traceback handler globally.


TEST_FILE_PATH = "/Users/russellocean/Dev/test/test_file.txt"
RENAMED_TEST_FILE_PATH = "/Users/russellocean/Dev/test/renamed_test_file.txt"


# Set the name of the index to use for the memory database.
index_name = "codebase-assistant"

# Create the global memory database.
memory_database = MemoryDatabase(index_name)


class TestTools(unittest.TestCase):
    def test_search(self):
        query = "Python programming"
        results = search(query)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    # Test all file tools in one test.
    def test_file_tools(self):
        try:
            # Create file.
            content = "This is a test file."
            create_file(TEST_FILE_PATH, content, memory_database)

            result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
            rprint("[bold green]========= Create File =========")
            rprint("Expected content: This is a test file.")
            rprint("Actual result:")
            create_table = Table(title="Create File")
            create_table.add_column("ID")
            create_table.add_column("Metadata")
            create_table.add_column("Score")
            create_table.add_column("Values")
            for res in result:
                create_table.add_row(
                    res["id"],
                    str(res["metadata"]),
                    str(res["score"]),
                    str(res["values"]),
                )
            rprint(create_table)

            # View file.
            content = view_file(TEST_FILE_PATH, memory_database)
            result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
            rprint("[bold yellow]========= View File =========")
            rprint("Expected content: This is a test file.")
            rprint("Actual result:")
            view_table = Table(title="View File")
            view_table.add_column("ID")
            view_table.add_column("Metadata")
            view_table.add_column("Score")
            view_table.add_column("Values")
            for res in result:
                view_table.add_row(
                    res["id"],
                    str(res["metadata"]),
                    str(res["score"]),
                    str(res["values"]),
                )
            rprint(view_table)

            # Rename file.
            rename_file(TEST_FILE_PATH, RENAMED_TEST_FILE_PATH, memory_database)
            result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
            rprint("[bold blue]========= Rename File =========")
            rprint(f"Expected file to be renamed to: {RENAMED_TEST_FILE_PATH}")
            rprint("Actual result:")
            rename_table = Table(title="Rename File")
            rename_table.add_column("ID")
            rename_table.add_column("Metadata")
            rename_table.add_column("Score")
            rename_table.add_column("Values")
            for res in result:
                rename_table.add_row(
                    res["id"],
                    str(res["metadata"]),
                    str(res["score"]),
                    str(res["values"]),
                )
            rprint(rename_table)

            # Delete file.
            delete_file(RENAMED_TEST_FILE_PATH, memory_database)
            result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
            rprint("[bold red]========= Delete File =========")
            rprint(f"Expected no file with path: {RENAMED_TEST_FILE_PATH}")
            rprint("Actual result:")
            delete_table = Table(title="Delete File")
            delete_table.add_column("ID")
            delete_table.add_column("Metadata")
            delete_table.add_column("Score")
            delete_table.add_column("Values")
            for res in result:
                delete_table.add_row(
                    res["id"],
                    str(res["metadata"]),
                    str(res["score"]),
                    str(res["values"]),
                )
            rprint(delete_table)

            # If all file tools were successful, then the result should be an empty list.
            self.assertEqual(result, [])

        except Exception as e:
            rprint("[bold red]An error occurred during the test:")
            rprint(e)

    # def test_view_file(self):
    #     content = "This is a test file."
    #     create_file(TEST_FILE_PATH, content, memory_database)

    #     content = view_file(TEST_FILE_PATH, memory_database)
    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
    #     # Print the result to the console.
    #     print(f"Test view_file result: {result}")
    #     self.assertEqual(content, "This is a test file.")
    #     os.remove(TEST_FILE_PATH)

    def test_calculate(self):
        expression = "2 + 3 * 4"
        result = calculate(expression)
        self.assertEqual(result, "14")

    # def test_create_file(self):
    #     content = "This is a test file."
    #     create_file(TEST_FILE_PATH, content, memory_database)
    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
    #     # Print the result to the console.
    #     print(f"Test create_file result: {result}")
    #     self.assertTrue(os.path.exists(TEST_FILE_PATH))
    #     os.remove(TEST_FILE_PATH)

    # def test_delete_file(self):
    #     with open(TEST_FILE_PATH, "w") as file:
    #         file.write("This is a test file.")

    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
    #     # Print the result to the console.
    #     print(f"Test delete_file result (pre delete): {result}")

    #     delete_file(TEST_FILE_PATH, memory_database)

    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)

    #     # Print the result to the console.
    #     print(f"Test delete_file result (post delete): {result}")

    #     self.assertFalse(os.path.exists(TEST_FILE_PATH))

    # def test_rename_file(self):
    #     content = "This is a test file."
    #     create_file(TEST_FILE_PATH, content, memory_database)

    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)
    #     # Print the result to the console.
    #     print(f"Test rename_file result (pre rename): {result}")

    #     rename_file(TEST_FILE_PATH, RENAMED_TEST_FILE_PATH, memory_database)
    #     result = memory_database.query_memories(f"file-{TEST_FILE_PATH}", top_k=1)

    #     # Print the result to the console.
    #     print(f"Test rename_file result (post rename): {result}")
    #     self.assertTrue(os.path.exists(RENAMED_TEST_FILE_PATH))
    #     os.remove(RENAMED_TEST_FILE_PATH)

    # Add more test cases for other functions as needed


if __name__ == "__main__":
    unittest.main()
