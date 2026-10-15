import pickle
from pathlib import Path


embedding_file = Path("embeddings") / "embeddings.pkl"


if not embedding_file.exists():
    print("Embeddings file not found.")

else:

    with open(embedding_file, "rb") as file:
        data = pickle.load(file)

    print("\nRegistered Users:")
    print("-" * 30)

    for user_name, embeddings in data.items():

        print(
            f"{user_name}: "
            f"{len(embeddings)} embeddings"
        )

    print("-" * 30)