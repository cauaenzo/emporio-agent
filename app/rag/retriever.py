
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import VECTOR_STORE_DIR
from app.rag.ingestion import PDFIngestion


class PolicyRetriever:
    """Recupera trechos do manual usando busca híbrida com RRF."""

    MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
    RRF_K = 60

    def __init__(self):
        self.ingestion = PDFIngestion()
        self.model = SentenceTransformer(self.MODEL_NAME)

        self.index = None
        self.chunks = []

        self.word_vectorizer = None
        self.word_matrix = None

        self.char_vectorizer = None
        self.char_matrix = None

    def _build_lexical_indexes(self):
        texts = [chunk["text"] for chunk in self.chunks]

        self.word_vectorizer = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            lowercase=True,
            strip_accents="unicode",
        )

        self.word_matrix = self.word_vectorizer.fit_transform(texts)

        self.char_vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            lowercase=True,
            strip_accents="unicode",
        )

        self.char_matrix = self.char_vectorizer.fit_transform(texts)

    def build_index(self):
        self.chunks = self.ingestion.create_chunks()

        if not self.chunks:
            raise ValueError("Nenhum conteúdo encontrado no manual.")

        texts = [chunk["text"] for chunk in self.chunks]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        embeddings = np.asarray(embeddings, dtype="float32")

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

        self._build_lexical_indexes()

        return len(self.chunks)

    def save_index(self):
        if self.index is None:
            raise ValueError("O índice ainda não foi construído.")

        VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

        faiss.write_index(
            self.index,
            str(VECTOR_STORE_DIR / "policies.index"),
        )

        with (VECTOR_STORE_DIR / "chunks.json").open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.chunks,
                file,
                ensure_ascii=False,
                indent=4,
            )

    def load_index(self):
        index_path = VECTOR_STORE_DIR / "policies.index"
        metadata_path = VECTOR_STORE_DIR / "chunks.json"

        if not index_path.is_file() or not metadata_path.is_file():
            raise FileNotFoundError(
                "Índice não encontrado. Construa o índice primeiro."
            )

        self.index = faiss.read_index(str(index_path))

        with metadata_path.open("r", encoding="utf-8") as file:
            self.chunks = json.load(file)

        if self.index.ntotal != len(self.chunks):
            raise ValueError(
                "Índice e metadados possuem tamanhos diferentes."
            )

        self._build_lexical_indexes()

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict]:

        if not query or not query.strip():
            return []

        if top_k < 1:
            raise ValueError("top_k deve ser maior que zero.")

        if self.index is None:
            raise ValueError("O índice ainda não foi carregado.")

        if not self.chunks:
            return []

        if self.word_vectorizer is None:
            self._build_lexical_indexes()

        query = query.strip()

        # 1. Ranking semântico
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32",
        )

        dense_scores, dense_indices = self.index.search(
            query_embedding,
            len(self.chunks),
        )

        # 2. Ranking lexical por palavras
        word_query = self.word_vectorizer.transform([query])

        word_scores = cosine_similarity(
            word_query,
            self.word_matrix,
        )[0]

        word_indices = np.argsort(word_scores)[::-1]

        # 3. Ranking lexical por caracteres
        char_query = self.char_vectorizer.transform([query])

        char_scores = cosine_similarity(
            char_query,
            self.char_matrix,
        )[0]

        char_indices = np.argsort(char_scores)[::-1]

        # 4. Fusão dos rankings usando Reciprocal Rank Fusion
        rankings = [
            dense_indices[0].tolist(),
            word_indices.tolist(),
            char_indices.tolist(),
        ]

        rrf_scores = {}

        for ranking in rankings:
            for rank, position in enumerate(ranking, start=1):
                contribution = 1 / (self.RRF_K + rank)

                rrf_scores[position] = (
                    rrf_scores.get(position, 0) + contribution
                )

        ordered_positions = sorted(
            rrf_scores,
            key=rrf_scores.get,
            reverse=True,
        )

        results = []

        for position in ordered_positions[:top_k]:
            chunk = self.chunks[position]

            results.append({
                "text": chunk["text"],
                "pages": chunk["pages"],
                "score": rrf_scores[position],
                "dense_score": float(dense_scores[0][
                    np.where(dense_indices[0] == position)[0][0]
                ]),
                "word_score": float(word_scores[position]),
                "char_score": float(char_scores[position]),
            })

        return results
