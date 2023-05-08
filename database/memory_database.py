import os
from typing import Any, Dict, List, Optional

import openai
import pinecone
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV")

openai_embeddings = OpenAIEmbeddings()
embed_model = "text-embedding-ada-002"


class MemoryDatabase:
    def __init__(self, index_name: str):
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
        if index_name not in pinecone.list_indexes():
            print(f"Creating index {index_name}...")
            pinecone.create_index(index_name, dimension=1536, metric="cosine")
        # Connect to index
        self.index = pinecone.Index(index_name)
        # View index stats
        # print(f"Index stats for {index_name}:")
        # print(self.index.describe_index_stats())
        # self.pinecone = pinecone.deinit()

    def __del__(self):
        # pinecone.delete_index(index_name)
        ...

    def create_embeddings(self, inputs: List[str]) -> List[List[float]]:
        embeddings = []
        for input_text in inputs:
            # response = self.openai.Embed.create(model="text-embedding-ada-002", input=input_text)
            # response = openai_embeddings.embed_query(input_text)
            response = openai.Embedding.create(input=[input_text], engine=embed_model)
            embeddings.append(response["data"][0]["embedding"])
        return embeddings

    def store_memories(self, memories: List[dict]):
        embeddings = self.create_embeddings([memory["content"] for memory in memories])
        # Create a list of tuples to store vector information
        vector_data = []
        for memory, embedding in zip(memories, embeddings):
            metadata = memory["metadata"].copy()
            metadata["content"] = memory["content"]
            vector_data.append((memory["id"], embedding, metadata))

        # Use the upsert function with the list of tuples
        self.index.upsert(vector_data)

    def query_memories(self, query: str, top_k: int = 5) -> List[dict]:
        embedding = self.create_embeddings([query])[0]
        results = self.index.query(
            vector=embedding, top_k=top_k, include_metadata=True, include_values=True
        )
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


def main():
    index_name = "codebase-assistant"

    memory_database = MemoryDatabase(index_name)

    # Store some example programming tasks
    programming_tasks = [
        {
            "id": "1",
            "content": "Implement a function to reverse a string in Python",
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

    print("Deleting index...")

    # Delete the index
    pinecone.delete_index(index_name)

    print("Done!")


if __name__ == "__main__":
    main()
