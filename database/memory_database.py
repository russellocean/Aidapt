import hashlib
import json
import os
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# Load the variables from the .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "memory_collection"

embed_model = "text-embedding-ada-002"


class MemoryDatabase:
    """
    A class to represent a memory database using Chroma.

    ...

    Attributes
    ----------
    client : chromadb.Client
        the Chroma client object
    collection : chromadb.Collection
        the Chroma collection object

    Methods
    -------
    close():
        Deletes the Chroma collection.
    get_next_id() -> str:
        Generates a new unique integer ID.
    store_memories(memories: List[dict]):
        Stores the given memories in the collection.
    stringify_content(content) -> str:
        Converts the given content into a string.
    query_memories(query: str = None, id: str = None, top_k: int = 5, threshold: float = None) -> List[dict]:
        Queries the collection and returns the results.
    update_memory(memory_id: str, new_content: Optional[str] = None, new_metadata: Optional[Dict[str, Any]] = None):
        Updates a memory in the collection.
    delete_memory(memory_id: str):
        Deletes a memory from the collection.
    clear_all_memories():
        Deletes all memories from the collection.
    query_relevant_memories(task: str, message: str, threshold: float = 0.7, top_k: int = 5) -> List[str]:
        Queries the collection for memories relevant to the given task and message.
    add_file_memory(file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        Adds a memory for a file to the collection.
    fetch(memory_id: str) -> Dict[str, Any]:
        Fetches a memory from the collection by ID.
    """

    def __init__(self):
        """Initializes a new MemoryDatabase object."""
        client_settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=".chromadb/",
        )
        self.client = chromadb.Client(client_settings)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

        # Try inserting a dummy document to trigger index creation
        self.collection.upsert(
            documents=["dummy document"],
            metadatas=[{"dummy": "metadata"}],
            ids=["dummy_id"],
        )
        self.collection.delete(ids=["dummy_id"])  # remove the dummy document

    def close(self):
        """Deletes the Chroma collection."""
        self.client.delete_collection(name=COLLECTION_NAME)

    def get_next_id(self) -> str:
        """Generates a new unique integer ID."""
        ids = [str(idx) for idx, doc in enumerate(self.collection.peek()["documents"])]
        max_int_id = max(int(id) for id in ids if id.isdigit())
        return str(max_int_id + 1)

    def store_memories(self, memories: List[dict]):
        """Stores the given memories in the collection."""

        # Prepare the data for adding to the collection
        documents = []
        metadatas = []
        ids = []

        for memory in memories:
            # Create a copy of the metadata and add the content
            metadata = memory.get("metadata", {}).copy()
            metadata["content"] = memory["content"]

            # Append the data to the corresponding lists
            documents.append(memory["content"])
            metadatas.append(metadata)

            # If an ID is provided, append it to the IDs list
            if "id" in memory:
                ids.append(memory["id"])

        # Add the data to the collection
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids if ids else None,
        )

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
        self, query: str = None, id: str = None, top_k: int = 5
    ) -> List[dict]:
        """Queries the collection and returns the results."""

        if self.collection.count() < top_k:
            top_k = self.collection.count()

        if query is not None:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["documents", "metadatas"],
            )
        elif id is not None:
            results = self.collection.get(ids=[id], include=["documents", "metadatas"])
        else:
            raise ValueError("You must provide either 'query' or 'id'.")

        return results

    def update_memory(
        self,
        memory_id: str,
        new_content: Optional[str] = None,
        new_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Updates a memory in the collection."""
        update_data = {}

        if new_content:
            update_data["documents"] = [new_content]

        if new_metadata:
            update_data["metadatas"] = [new_metadata]

        if new_content or new_metadata:
            self.collection.upsert(
                ids=[memory_id],
                metadatas=update_data.get("metadatas"),
                documents=update_data.get("documents"),
            )

    def delete_memory(self, memory_id: str):
        """Deletes a memory from the collection."""
        try:
            result = self.collection.delete(ids=[memory_id])

            if not result:
                return f"No memories were deleted. Check if memory with id {memory_id} exists."

            return f"Successfully deleted memory with id: {memory_id}"

        except Exception as e:
            return f"Error in delete_memory: {str(e)}"

    def clear_all_memories(self):
        """Deletes all memories from the collection."""
        self.client.delete_collection(name=COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
        )

    def query_relevant_memories(
        self, task: str, message: str, top_k: int = 5
    ) -> List[str]:
        """
        Queries the collection for memories relevant to the given task and message.

        Args:
            task (str): The task for which to search relevant memories.
            message (str): The message for which to search relevant memories.
            include_files (bool, optional): Whether to include files in the search. Defaults to False.
            threshold (float, optional): The minimum score for a memory to be considered relevant. Defaults to 0.7.
            top_k (int, optional): The number of relevant memories to return. Defaults to 5.

        Returns:
            List[str]: The list of relevant memories.
        """
        if self.collection.count() < top_k:
            top_k = self.collection.count()

        query = f"{task} {message}"
        results = self.query_memories(query, top_k=top_k)

        relevant_memories = []
        for idx in range(len(results["ids"])):
            memory_str = f"ID: {results['ids'][idx]}, Content: {results['documents'][idx]}, Metadata: {results['metadatas'][idx]}"
            relevant_memories.append(memory_str)

        return relevant_memories

    def add_file_memory(
        self, file_path: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ):
        """Adds a memory for a file to the collection."""

        # Generate a unique ID from the file name using SHA-256 hash function
        # Convert the SHA-256 hash to an integer and take modulus to keep the result in a reasonable range
        sha256_hash = hashlib.sha256(file_path.encode()).hexdigest()
        memory_id = int(sha256_hash, 16) % 10**12

        # ChromaDB expects IDs to be strings, so convert the memory ID to a string
        memory_id = str(memory_id)

        memory_content = f"File: {file_path}, Content: {content}"
        if metadata is None:
            metadata = {}
        metadata["file_path"] = file_path

        memory = {"id": memory_id, "content": memory_content, "metadata": metadata}
        self.store_memories([memory])

    def search_file(self, file_path: str) -> List[dict]:
        """Searches for a file in the collection by its file path metadata.

        Args:
            file_path (str): The file path to search for.

        Returns:
            List[dict]: The results of the search.
        """

        # Get the ID of the file with the specified file_path
        file_id = self.get_id_from_filepath(file_path)

        # If the ID was found, get the file data using the ID
        if file_id:
            return self.collection.get(ids=[file_id])

        # If no ID was found, return an empty list
        return []

    def get_id_from_filepath(self, file_path: str) -> str:
        all_documents = self.collection.get()

        # Get the list of metadatas from the dictionary
        metadatas = all_documents["metadatas"]
        ids = all_documents["ids"]

        # Iterate over the metadatas list
        for i, metadata in enumerate(metadatas):
            if isinstance(metadata, dict) and "file_path" in metadata:
                if metadata["file_path"] == file_path:
                    return ids[i]

        return None

    def format_query_results(self, query_result):
        formatted_result = ""

        # Get IDs, documents, and metadata # Default to empty list if key not present
        ids = query_result.get("ids", [[]])[0]
        documents = query_result.get("documents", [[]])[0]
        metadatas = query_result.get("metadatas", [[]])[0]

        # Ensure that the lengths of IDs, documents, and metadatas are the same
        if len(ids) == len(documents) == len(metadatas):
            # Iterate over the items
            for id, doc, metadata in zip(ids, documents, metadatas):
                formatted_result += f"ID: {id}\n"
                formatted_result += f"Document: {doc}\n"
                if metadata:
                    formatted_result += "Metadata:\n"
                    for key, value in metadata.items():
                        # Skip if 'content' or 'file_path' field from metadata is already present in the document
                        if (
                            (key == "content" or key == "file_path")
                            and value not in doc
                        ) or key not in ["content", "file_path"]:
                            formatted_result += f"\t{key}: {value}\n"
                else:
                    formatted_result += "Metadata: None\n"
                formatted_result += (
                    "\n"  # Add a new line after each item for readability
                )
        else:
            formatted_result = (
                "Error: The lengths of IDs, documents, and metadatas do not match."
            )

        return formatted_result


def main():
    from rich import print
    from rich.table import Table

    def pretty_print_memory(memory):
        """Helper function to pretty print memory data."""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID")
        table.add_column("Document")
        table.add_column("Metadata")

        documents = memory["documents"]
        metadatas = memory["metadatas"]

        for idx in range(len(documents)):
            document = documents[idx]
            metadata = metadatas[idx] if idx < len(metadatas) else None
            table.add_row(str(idx), str(document), str(metadata))

        print(table)

    # Initialize the memory database
    memory_db = MemoryDatabase()
    memory_db.clear_all_memories()

    # Print initial state
    print("Initial state:")
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Store some memories
    print("Storing memories:")
    memories = [
        {"id": "1", "content": "This is a memory."},
        {"id": "2", "content": "This is another memory.", "metadata": {"tag": "test"}},
    ]
    memory_db.store_memories(memories)
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Query some memories
    print("Querying memories:")
    query_results = memory_db.query_memories(query="memory")
    pretty_print_memory(query_results)
    print("\n")

    # Update a memory
    print("Updating a memory:")
    memory_db.update_memory(
        memory_id="1",
        new_content="This is an updated memory.",
        new_metadata={"tag": "updated"},
    )
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Delete a memory
    print("Deleting a memory:")
    memory_db.delete_memory(memory_id="1")
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Clear all memories
    print("Clearing all memories:")
    memory_db.clear_all_memories()
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Add file memory
    print("Adding file memory:")
    memory_db.add_file_memory(file_path="file.txt", content="This is file content.")
    pretty_print_memory(memory_db.collection.peek())
    print("\n")

    # Fetch a memory
    print("Fetching a memory:")
    # fetched_memory = memory_db.fetch(memory_id="file-file.txt")
    # print(fetched_memory)
    # print("\n")

    # Close the database
    memory_db.close()


if __name__ == "__main__":
    main()
