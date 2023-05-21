import unittest

from rich import print as rprint
from rich.table import Table
from rich.traceback import install

from agents.agent import Agent
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


# Create the global memory database.
memory_database = MemoryDatabase()

# Set the memory database for the Agent class.
Agent.set_memory_database(memory_database)


def create_table_from_result(title, result):
    table = Table(title=title)
    table.add_column("ID")
    table.add_column("Metadata")
    table.add_column("Values")
    for idx, doc, meta in zip(
        result["ids"][0], result["documents"][0], result["metadatas"][0]
    ):
        table.add_row(
            str(idx),
            str(doc),
            str(meta),
        )
    return table


class TestTools(unittest.TestCase):
    def test_search(self):
        query = "Python programming"
        results = search(query)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_file_tools(self):
        # Create file.
        print(
            create_file(
                TEST_FILE_PATH,
            )
        )

        result = memory_database.query_memories(TEST_FILE_PATH, top_k=1)
        rprint("[bold green]========= Create File =========")
        rprint("Expected content: This is a test file.")
        rprint("Actual result:")
        rprint(create_table_from_result("Create File", result))

        # View file.
        view_file(TEST_FILE_PATH)
        result = memory_database.query_memories(TEST_FILE_PATH, top_k=1)
        rprint("[bold yellow]========= View File =========")
        rprint("Expected content: This is a test file.")
        rprint("Actual result:")
        rprint(create_table_from_result("View File", result))

        print(f"file_path: {memory_database.query_memories(TEST_FILE_PATH)}")

        # Rename file.
        rename_file(TEST_FILE_PATH, RENAMED_TEST_FILE_PATH)
        result = memory_database.query_memories(TEST_FILE_PATH, top_k=1)
        rprint("[bold blue]========= Rename File =========")
        rprint(f"Expected file to be renamed to: {RENAMED_TEST_FILE_PATH}")
        rprint("Actual result:")
        rprint(create_table_from_result("Rename File", result))

        # Delete file.
        delete_file(RENAMED_TEST_FILE_PATH)
        result = memory_database.query_memories(TEST_FILE_PATH, top_k=1)
        rprint("[bold red]========= Delete File =========")
        rprint(f"Expected no file with path: {RENAMED_TEST_FILE_PATH}")
        rprint("Actual result:")
        rprint(create_table_from_result("Delete File", result))

        # If all file tools were successful, then the result should be an empty list.
        self.assertEqual(result, [])

    def test_calculate(self):
        expression = "2 + 3 * 4"
        result = calculate(expression)
        self.assertEqual(result, "14")

    def create_table_from_result(title, result):
        table = Table(title=title)
        table.add_column("ID")
        table.add_column("Metadata")
        table.add_column("Values")
        for idx, doc, meta in zip(
            result["ids"][0], result["documents"][0], result["metadatas"][0]
        ):
            table.add_row(
                str(idx),
                str(doc),
                str(meta),
            )
        return table


if __name__ == "__main__":
    unittest.main()
