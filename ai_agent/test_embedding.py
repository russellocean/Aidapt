from ai_agent.external_apis import get_embedding


def main():
    text = "def example_function():\n    pass"
    embedding = get_embedding(text)
    print(f"Text: {text}")
    print(f"Embedding: {embedding}")


if __name__ == "__main__":
    main()
