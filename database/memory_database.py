import json
import os
import time
from typing import Any, Dict, List, Optional

import openai
import pinecone
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

embed_model = "text-embedding-ada-002"


class MemoryDatabase:
    """
    A class to represent a memory database using Pinecone.

    ...

    Attributes
    ----------
    index_name : str
        the name of the Pinecone index
    index : pinecone.Index
        the Pinecone index object
    ids : set
        a set of all the IDs in the index

    Methods
    -------
    close():
        Deletes the Pinecone index.
    create_embeddings(inputs: List[str]) -> List[List[float]]:
        Creates embeddings for the given input strings.
    get_next_id() -> str:
        Generates a new unique integer ID.
    store_memories(memories: List[dict]):
        Stores the given memories in the index.
    stringify_content(content) -> str:
        Converts the given content into a string.
    query_memories(query: str = None, id: str = None, top_k: int = 5, threshold: float = None) -> List[dict]:
        Queries the index and returns the results.
    update_memory(memory_id: str, new_content: Optional[str] = None, new_metadata: Optional[Dict[str, Any]] = None):
        Updates a memory in the index.
    delete_memory(memory_id: str):
        Deletes a memory from the index.
    clear_all_memories():
        Deletes all memories from the index.
    query_relevant_memories(task: str, message: str, threshold: float = 0.7, top_k: int = 5) -> List[str]:
        Queries the index for memories relevant to the given task and message.
    add_file_memory(file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        Adds a memory for a file to the index.
    fetch(memory_id: str) -> Dict[str, Any]:
        Fetches a memory from the index by ID.
    """

    def __init__(self, index_name: str):
        """Initializes a new MemoryDatabase object."""
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        if index_name not in pinecone.list_indexes():
            print(f"Creating index {index_name}...")
            pinecone.create_index(index_name, dimension=1536, metric="cosine")
            # Wait an additional 5 seconds for the index to be created
            time.sleep(5)  # wait for 5 seconds
        elif index_name in pinecone.list_indexes():
            print(f"Index {index_name} already exists. Deleting and recreating...")
            pinecone.delete_index(index_name)
            print(f"Creating index {index_name}...")
            pinecone.create_index(index_name, dimension=1536, metric="cosine")
            # Wait an additional 5 seconds for the index to be created
            time.sleep(5)  # wait for 5 seconds

        # Connect to index
        self.index_name = index_name
        self.index = pinecone.Index(index_name)

        self.ids = set()  # used to store all the IDs

    def close(self):
        """Deletes the Pinecone index."""
        pinecone.delete_index(self.index_name)

    def create_embeddings(self, inputs: List[str]) -> List[List[float]]:
        """Creates embeddings for the given input strings."""
        embeddings = []
        for input_text in inputs:
            # response = self.openai.Embed.create(model="text-embedding-ada-002", input=input_text)
            response = openai.Embedding.create(input=[input_text], engine=embed_model)
            embeddings.append(response["data"][0]["embedding"])
        return embeddings

    def get_next_id(self):
        """Generates a new unique integer ID."""
        max_int_id = max(int(id) for id in self.ids if id.isdigit())
        return str(max_int_id + 1)

    def store_memories(self, memories: List[dict]):
        """Stores the given memories in the index."""
        non_empty_memories = [memory for memory in memories if memory["content"]]
        embeddings = self.create_embeddings(
            [memory["content"] for memory in non_empty_memories]
        )

        # Create a list of tuples to store vector information
        vector_data = []
        for memory, embedding in zip(memories, embeddings):
            # Create a copy of the metadata and add the content
            metadata = memory.get("metadata", {}).copy()
            metadata["content"] = memory["content"]

            # If no ID is provided, generate a new one
            memory_id = memory.get("id")
            if memory_id is None:
                memory_id = self.get_next_id()
            # Convert the memory id to a string
            memory_id_str = str(memory_id)

            # Add the new ID to the set of IDs
            self.ids.add(memory_id_str)

            vector_data.append((memory_id_str, embedding, metadata))
        # Use the upsert function with the list of tuples
        self.index.upsert(vector_data)

    def stringify_content(self, content):
        """Converts the given content into a string."""
        if isinstance(content, dict):
            return json.dumps(content)
        elif isinstance(content, list):
            return (
                json.dumps(content)
                if all(isinstance(i, dict) for i in content)
                else " ".join(map(str, content))
            )
        else:
            return str(content)

    def query_memories(
        self, query: str = None, id: str = None, top_k: int = 5, threshold: float = None
    ) -> List[dict]:
        """Queries the index and returns the results."""
        if query is not None:
            embedding = self.create_embeddings([query])[0]
            results = self.index.query(
                vector=embedding,
                top_k=top_k,
                include_metadata=True,
                include_values=False,
            )
        elif id is not None:
            results = self.index.query(
                id=id, top_k=top_k, include_metadata=True, include_values=False
            )
        else:
            raise ValueError("You must provide either 'query' or 'id'.")

        if threshold is not None:
            results.matches = [
                result for result in results.matches if result["score"] >= threshold
            ]
        return results.matches

    def update_memory(
        self,
        memory_id: str,
        new_content: Optional[str] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Updates a memory in the index."""
        """
        Currently the update function does not work. However the upsert function does work, and behaves the same if the id already exists.
        TODO - Fix the update function
        """
        if new_content:
            new_embedding = self.create_embeddings([new_content])[0]
            self.index.update(id=memory_id, values=new_embedding)

        if new_metadata:
            self.index.update(id=memory_id, set_metadata=new_metadata)

    def delete_memory(self, memory_id: str):
        """Deletes a memory from the index."""
        self.index.delete(ids=[memory_id])
        # Also remove the deleted ID from the set of IDs
        self.ids.remove(memory_id)

    def clear_all_memories(self):
        """Deletes all memories from the index."""
        for memory_id in list(self.ids):  # iterate over a copy of the set
            self.delete_memory(memory_id)

    def query_relevant_memories(
        self,
        task: str,
        message: str,
        include_files: bool = False,
        threshold: float = 0.7,
        top_k: int = 5,
    ) -> List[str]:
        """
        TODO - Eventually when we receive a higher token model we should include file search again. Currently files are too large to be included in the search.

        Queries the index for memories relevant to the given task and message. It excludes
        memories with IDs that have a file prefix unless include_files is set to True.

        Args:
            task (str): The task for which to search relevant memories.
            message (str): The message for which to search relevant memories.
            include_files (bool, optional): Whether to include files in the search. Defaults to False.
            threshold (float, optional): The minimum score for a memory to be considered relevant. Defaults to 0.7.
            top_k (int, optional): The number of relevant memories to return. Defaults to 5.

        Returns:
            List[str]: The list of relevant memories.
        """

        # Define the query and initial number of results to get
        # We need to fetch more results than top_k because we might exclude some
        query = f"{task} {message}"
        initial_top_k = top_k * 2  # Assume that at most half the results will be files

        # Query for initial_top_k memories
        results = self.query_memories(query, top_k=initial_top_k)

        relevant_memories = []
        for result in results:
            # Only include the result if it is above the threshold and doesn't start with 'file-', unless include_files is True
            if result["score"] >= threshold and (
                include_files or not result["id"].startswith("file-")
            ):
                metadata = result["metadata"]
                memory_str = f"  ID: {result['id']}, Content: {metadata['content']}, Metadata: {metadata}, Score: {result['score']}"
                relevant_memories.append(memory_str)

                # Stop appending to relevant_memories if we already have top_k entries
                if len(relevant_memories) == top_k:
                    break

        return relevant_memories

    def add_file_memory(
        self, file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Adds a memory for a file to the index."""
        memory_id = f"file-{file_path}"
        memory_content = f"File: {file_path}, Content: {content}"
        if metadata is None:
            metadata = {}
        metadata["file_path"] = file_path

        memory = {"id": memory_id, "content": memory_content, "metadata": metadata}
        self.store_memories([memory])

    def fetch(self, memory_id: str):
        """Fetches a memory from the index by ID."""
        return self.index.fetch(ids=[memory_id])


def main():
    index_name = "codebase-assistant"

    memory_database = MemoryDatabase(index_name)

    # Store some example programming tasks
    programming_tasks = [
        {
            "id": "file-test.py",
            "content": "from typing import List\n\n\ndef reverse_string(string: str) -> str:\n    return string[::-1]\n\n\nif __name__ == '__main__':\n    print(reverse_string('Hello World'))",
            "metadata": {"language": "Python"},
        },
        {
            "id": "2",
            "content": "Create a function to find the factorial of a number using recursion",
            "metadata": {"language": "Python"},
        },
        {
            "id": "3",
            "content": "Write a program to find the largest element in an array",
            "metadata": {"language": "Python"},
        },
        {
            "id": "4",
            "content": "Create a function to calculate the Fibonacci sequence using dynamic programming",
            "metadata": {"language": "Python"},
        },
        {
            "id": "5",
            "content": "Implement a function to sort a list of integers using the bubble sort algorithm",
            "metadata": {"language": "Python"},
        },
    ]

    memory_database.store_memories(programming_tasks)

    # Query the database for relevant programming tasks
    queries = [
        "How to reverse a string in Python?",
        "What is the best way to calculate the Fibonacci sequence?",
        "How can I sort a list of numbers in Python?",
        "What is the first ID in the database?",
    ]

    for query in queries:
        print(f"Query: {query}")
        matches = memory_database.query_memories(query)
        print("Matches:")
        for match in matches:
            print(
                f"  ID: {match['id']}, Content: {match['metadata']['content']}, Score: {match['score']}"
            )
        print()

    print("Updating memory...")

    # Update the content and metadata of a memory
    memory_database.update_memory(
        memory_id="1",
        new_content="Implement a function to reverse a string in Python 3",
        new_metadata={"language": "Python 3"},
    )

    new_programming_tasks = [
        {
            "id": "1",
            "content": "Implement a function to reverse a string in Python 3",
            "metadata": {"language": "Python 3"},
        },
    ]

    # At the moment it appears that pinecones update update function does not work. However the upsert function does work, and behaves the same if the id already exists.
    memory_database.store_memories(new_programming_tasks)

    # Query the updated memory
    query = "How to reverse a string in Python?"
    print(f"Query: {query}")
    matches = memory_database.query_memories(query)
    print("Matches:")
    for match in matches:
        print(
            f"  ID: {match['id']}, Content: {match['metadata']['content']}, Score: {match['score']}"
        )

    print("Deleting memory...")

    # Delete a memory
    memory_database.delete_memory("1")

    # Query the deleted memory
    query = "How to reverse a string in Python?"
    print(f"Query: {query}")
    matches = memory_database.query_memories(query)
    print("Matches:")
    for match in matches:
        print(
            f"  ID: {match['id']}, Content: {match['metadata']['content']}, Score: {match['score']}"
        )

    fetch = memory_database.query_memories(id="file-test.py")
    print(f"Fetch by id: {fetch}")

    print("Deleting index...")

    # Delete the index
    # Database gets deleted when the MemoryDatabase object is deleted
    # pinecone.delete_index(index_name)

    print("Done!")


if __name__ == "__main__":
    main()
