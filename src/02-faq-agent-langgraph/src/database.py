import chromadb
import re
from pathlib import Path

from dotenv import load_dotenv
from chromadb.utils import embedding_functions

load_dotenv(override=True)


class FAQDatabase:
    def __init__(self, collection_name: str = "faq_collection"):
        """Initialize ChromaDB with OpenAI embeddings"""
        self.client = chromadb.Client()
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            model_name="text-embedding-3-small"
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_function
        )

    def _parse_markdown(self, content: str) -> list[dict]:
        """Parse markdown content and split by H2 sections"""
        chunks = []
        sections = re.split(r"##\s+", content)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            lines = section.split("\n", 1)
            title = lines[0].strip()
            body = lines[1].strip() if len(lines) > 1 else ""

            if title and body:
                chunks.append({"title": title, "content": f"## {title}\n\n{body}"})

        return chunks

    def _add_chunks(self, chunks: list[dict]) -> None:
        """Add chunks to ChromaDB collection"""
        if not chunks:
            return

        offset = self.collection.count()
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [{"title": chunk["title"]} for chunk in chunks]
        ids = [f"chunk_{offset + idx}" for idx in range(len(chunks))]

        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def load_document(self, file_path: str) -> None:
        """Load a single FAQ markdown document into ChromaDB"""
        content = Path(file_path).read_text()
        chunks = self._parse_markdown(content)
        self._add_chunks(chunks)
        print(f"Loaded {len(chunks)} sections from {Path(file_path).name}")

    def load_from_directory(self, documents_dir: str) -> None:
        """Load all FAQ markdown documents from a directory into ChromaDB"""
        doc_path = Path(documents_dir)
        all_chunks = []

        for md_file in doc_path.glob("*.md"):
            content = md_file.read_text()
            all_chunks.extend(self._parse_markdown(content))

        self._add_chunks(all_chunks)
        print(f"Loaded {len(all_chunks)} FAQ sections")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Semantic search for relevant FAQ sections"""
        results = self.collection.query(query_texts=[query], n_results=top_k)

        if not results["documents"][0]:
            return []

        return [
            {"title": metadata["title"], "content": doc, "distance": distance}
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
