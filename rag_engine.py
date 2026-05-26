import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class RAGEngine:
    def __init__(self, kb_path: str):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.chunks = self._load_and_chunk(kb_path)
        self.index, self.embeddings = self._build_index()

    def _load_and_chunk(self, path: str) -> list[str]:
        """
        Load + Chunk
        โหลด knowledge base แล้วแบ่งเป็น chunk ตามบรรทัดว่าง
        """
        with open(path, encoding="utf-8") as file:
            text = file.read()

        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

        if not chunks:
            raise ValueError("ไม่พบข้อมูลใน knowledge base")

        return chunks

    def _build_index(self):
        """
        Embed
        แปลง chunk เป็น vector แล้วเก็บใน FAISS index
        """
        embeddings = self.model.encode(self.chunks, show_progress_bar=False)

        embeddings_np = np.array(embeddings, dtype="float32")

        index = faiss.IndexFlatL2(embeddings_np.shape[1])
        index.add(embeddings_np)

        return index, embeddings_np

    def search(self, query: str, top_k: int = 3) -> list[str]:
        """
        Search
        ค้นหา chunk ที่ใกล้เคียงกับคำถามมากที่สุด
        """
        query_embedding = self.model.encode([query])
        query_np = np.array(query_embedding, dtype="float32")

        distances, indices = self.index.search(query_np, top_k)

        results = []

        for index_id in indices[0]:
            if 0 <= index_id < len(self.chunks):
                results.append(self.chunks[index_id])

        return results