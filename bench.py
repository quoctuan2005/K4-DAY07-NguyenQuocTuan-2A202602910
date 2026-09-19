from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

from src import Document, EmbeddingStore, RecursiveChunker


DATA_DIR = Path("data/university") if Path("data/university").exists() else Path("data/hoc_bong")
GOLD_SET_PATH = Path("benchmark_gold_set.json")
TOP_K = 3


def tokenize(text: str) -> list[str]:
    return re.findall(r"[0-9A-Za-zÀ-ỹĐđ]+(?:[./-][0-9A-Za-zÀ-ỹĐđ]+)*", text.lower())


class LexicalEmbedder:
    """Small deterministic TF-IDF embedder for local benchmark runs."""

    def __init__(self, texts: list[str]) -> None:
        vocab = sorted({token for text in texts for token in tokenize(text)})
        self.index = {token: i for i, token in enumerate(vocab)}
        doc_count = max(1, len(texts))
        self.idf = [1.0] * len(self.index)
        for token, index in self.index.items():
            df = sum(1 for text in texts if token in set(tokenize(text)))
            self.idf[index] = math.log((doc_count + 1) / (df + 1)) + 1.0

    def __call__(self, text: str) -> list[float]:
        vec = [0.0] * len(self.index)
        for token in tokenize(text):
            if token in self.index:
                vec[self.index[token]] += 1.0
        vec = [value * self.idf[index] for index, value in enumerate(vec)]
        norm = math.sqrt(sum(value * value for value in vec))
        if norm == 0:
            return vec
        return [value / norm for value in vec]


class HeadingChunker:
    """Chunk by Markdown headings, with recursive fallback for long sections."""

    def __init__(self, max_chars: int = 1200) -> None:
        self.max_chars = max_chars
        self.fallback = RecursiveChunker(chunk_size=max_chars)

    def chunk(self, text: str) -> list[str]:
        sections: list[tuple[str, list[str]]] = []
        current_heading = ""
        current_lines: list[str] = []

        for line in text.splitlines():
            if re.match(r"^#{1,6}\s+", line):
                if current_heading or current_lines:
                    sections.append((current_heading, current_lines))
                current_heading = line.strip()
                current_lines = []
            else:
                current_lines.append(line)

        if current_heading or current_lines:
            sections.append((current_heading, current_lines))

        chunks: list[str] = []
        for heading, lines in sections:
            section = "\n".join([heading, *lines]).strip() if heading else "\n".join(lines).strip()
            if not section:
                continue
            if len(section) <= self.max_chars:
                chunks.append(section)
                continue

            body = "\n".join(lines).strip()
            for part in self.fallback.chunk(body):
                chunk = f"{heading}\n{part}".strip() if heading else part.strip()
                if chunk:
                    chunks.append(chunk)

        return chunks


def split_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---"):
        return {}, markdown
    _, frontmatter, body = markdown.split("---", 2)
    metadata: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("\"'")
    return metadata, body.strip()


def load_gold_set() -> list[dict[str, Any]]:
    return json.loads(GOLD_SET_PATH.read_text(encoding="utf-8"))


def load_corpus() -> list[tuple[Path, dict[str, str], str]]:
    corpus = []
    for path in sorted(DATA_DIR.glob("*.md")):
        metadata, content = split_frontmatter(path.read_text(encoding="utf-8"))
        corpus.append((path, metadata, content))
    return corpus


def build_documents(corpus: list[tuple[Path, dict[str, str], str]], chunker: HeadingChunker) -> list[Document]:
    docs: list[Document] = []
    for path, metadata, content in corpus:
        chunks = chunker.chunk(content)
        for index, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "doc_id": path.stem,
                "chunk_index": str(index),
                "source": str(path),
            }
            docs.append(Document(id=f"{path.stem}#{index}", content=chunk, metadata=chunk_metadata))
    return docs


def print_result(query_spec: dict[str, Any], results: list[dict[str, Any]]) -> None:
    print("=" * 88)
    print(f"Q{query_spec['id']}: {query_spec['query']}")
    print(f"Gold doc : {query_spec['gold_doc_id']}")
    print(f"Gold ans : {query_spec['gold_answer']}")
    print(f"Filter   : {query_spec.get('filter')}")
    print("Top-3:")
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        preview = re.sub(r"\s+", " ", result["content"]).strip()[:220]
        print(
            f"  {rank}. score={result['score']:.3f} "
            f"doc_id={metadata.get('doc_id')} chunk={metadata.get('chunk_index')} "
            f"audience={metadata.get('audience')}"
        )
        print(f"     {preview}")
    if not results:
        print("  Không có kết quả.")


def main() -> int:
    gold_set = load_gold_set()
    corpus = load_corpus()
    chunker = HeadingChunker(max_chars=1200)

    documents = build_documents(corpus, chunker)
    query_texts = [item["query"] for item in gold_set]
    embedder = LexicalEmbedder([doc.content for doc in documents] + query_texts)
    store = EmbeddingStore(collection_name="benchmark_university", embedding_fn=embedder)
    store.add_documents(documents)

    print("=== Benchmark CP5 ===")
    print(f"Corpus dir     : {DATA_DIR}")
    print(f"Gold set       : {GOLD_SET_PATH}")
    print(f"Chunker        : HeadingChunker(max_chars={chunker.max_chars})")
    print(f"Files loaded   : {len(corpus)}")
    print(f"Chunks loaded  : {store.get_collection_size()}")
    print()

    for query_spec in gold_set:
        results = store.search_with_filter(
            query_spec["query"],
            top_k=TOP_K,
            metadata_filter=query_spec.get("filter"),
        )
        print_result(query_spec, results)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
