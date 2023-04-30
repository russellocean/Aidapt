import os
from glob import glob

import faiss
import numpy as np
import openai
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

from database.file_parser import get_functions
from utils import print_search_results

embeddings = OpenAIEmbeddings()

# Load the variables from the .env file
load_dotenv()

# Access the variables using the os module
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class CodebaseDatabase:
    def __init__(self, project_folder):
        self.project_folder = project_folder
        self.documents = self.load_documents()
        self.faiss_index = self.create_vector_database()

    def load_documents(self):
        code_files = [
            y
            for x in os.walk(self.project_folder)
            for y in glob(os.path.join(x[0], "*.py"))
        ]
        all_funcs = []

        for code_file in code_files:
            funcs = list(get_functions(code_file))
            for func in funcs:
                all_funcs.append(func)

        print(f"Loaded {len(all_funcs)} functions from {len(code_files)} files.")
        return all_funcs

    def create_vector_database(self):
        embeddings = []

        print("Generating embeddings for loaded functions...")
        for document in self.documents:
            code = document["code"]
            embedding = get_embedding(code)
            embeddings.append(embedding)
        print("Embeddings generated.")

        # print("Embeddings of loaded functions:")
        # for i, embedding in enumerate(embeddings):
        #     print(f"{i + 1}: {embedding}")

        index = self.create_faiss_index(embeddings)
        return index

    def create_faiss_index(self, vectors):
        dimension = len(vectors[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(vectors).astype("float32"))
        return index

    def update_faiss_index(self, new_information):
        new_vector = get_embedding(new_information["code"])
        self.faiss_index.add(np.array([new_vector]).astype("float32"))

    def search_faiss_index(self, query, k=5):
        query_vector = get_embedding(query)
        distances, indices = self.faiss_index.search(
            np.array([query_vector]).astype("float32"), k
        )
        results = [
            {"document": self.documents[i], "distance": distances[0][j]}
            for j, i in enumerate(indices[0])
        ]
        return results


def convert_to_database(project_folder, project_source):
    if project_source != "none":
        codebase_database = CodebaseDatabase(project_folder)
    else:
        codebase_database = None
    return codebase_database


def get_embedding(text, engine="text-embedding-ada-002"):
    openai.api_key = OPENAI_API_KEY

    query_result = embeddings.embed_query(text)
    return query_result


def main():
    project_folder = "/Users/russellocean/Dev/ProjectGPT"
    codebase_database = CodebaseDatabase(project_folder)

    query = input("Enter your search query: ")
    results = codebase_database.search_faiss_index(query)

    print_search_results(query, results)


if __name__ == "__main__":
    main()
