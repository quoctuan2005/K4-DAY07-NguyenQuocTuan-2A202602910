from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            return "Không tìm thấy thông tin phù hợp trong cơ sở tri thức."

        context_blocks = []
        for i, r in enumerate(results, start=1):
            source = r["metadata"].get("source") or r["metadata"].get("doc_id") or r.get("id", "không rõ nguồn")
            context_blocks.append(f"[{i}] (Nguồn: {source}):\n{r['content']}")

        context_text = "\n\n".join(context_blocks)
        prompt = (
            f"Dựa vào ngữ cảnh dưới đây để trả lời câu hỏi. "
            f"Chỉ sử dụng thông tin được cung cấp, không suy đoán hay bịa đặt.\n\n"
            f"--- NGỮ CẢNH ---\n{context_text}\n\n"
            f"--- CÂU HỎI ---\n{question}\n\n"
            f"--- CÂU TRẢ LỜI ---"
        )
        return self.llm_fn(prompt)
