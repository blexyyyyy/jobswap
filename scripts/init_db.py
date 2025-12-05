from database.db_manager import init_db
from database.vector_store import VectorStore


def main() -> None:
    print("📦 Initializing SQLite database...")
    init_db()
    print("✅ Database initialized.")

    print("📦 Initializing ChromaDB vector store...")
    _ = VectorStore()
    print("✅ ChromaDB initialized (collections ready).")

    print("🎉 Foundation setup complete.")


if __name__ == "__main__":
    main()