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
    def __init__(self, index_name: str):
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
        # View index stats
        # print(f"Index stats for {index_name}:")
        # print(self.index.describe_index_stats())
        # self.pinecone = pinecone.deinit()

    # def __del__(self):
    #     pinecone.delete_index(self.index_name)

    def close(self):
        pinecone.delete_index(self.index_name)

    def create_embeddings(self, inputs: List[str]) -> List[List[float]]:
        embeddings = []
        for input_text in inputs:
            # response = self.openai.Embed.create(model="text-embedding-ada-002", input=input_text)
            response = openai.Embedding.create(input=[input_text], engine=embed_model)
            embeddings.append(response["data"][0]["embedding"])
        return embeddings

    def store_memories(self, memories: List[dict]):
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
            # Convert the memory id to a string
            memory_id_str = str(memory["id"])
            vector_data.append((memory_id_str, embedding, metadata))

        # Use the upsert function with the list of tuples
        self.index.upsert(vector_data)

    def stringify_content(self, content):
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
        self.index.delete(ids=[memory_id])

    def query_relevant_memories(
        self, task: str, message: str, threshold: float = 0.7, top_k: int = 5
    ) -> List[str]:
        query = f"{task} {message}"
        results = self.query_memories(query, top_k=top_k)

        relevant_memories = []
        for result in results:
            if result["score"] >= threshold:
                relevant_memories.append(
                    f"  ID: {result['id']}, Content: {result['metadata']['content']}, Score: {result['score']}"
                )

        return relevant_memories

    def add_file_memory(
        self, file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        memory_id = f"file-{file_path}"
        memory_content = f"File: {file_path}, Content: {content}"
        if metadata is None:
            metadata = {}
        metadata["file_path"] = file_path

        memory = {"id": memory_id, "content": memory_content, "metadata": metadata}
        self.store_memories([memory])

    def fetch(self, memory_id: str):
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
