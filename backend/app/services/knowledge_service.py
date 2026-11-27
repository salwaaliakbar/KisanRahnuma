"""Ask Anything: weighted keyword search over a predefined knowledge base.

Keywords cover English, Roman Urdu and Urdu/Sindhi script, so a question typed in any of
them finds the entry; the presenter then shows the answer in the farmer's language.
Only answers that reach the knowledge base's min_score are returned; otherwise the
caller shows a "not available" fallback. A RAG/LLM implementation can replace
`search` later without changing the conversation engine.
"""
from dataclasses import dataclass

from app.i18n import LocalizedText
from app.services.data_loader import load_json
from app.services.text_utils import tokens


@dataclass(frozen=True)
class KnowledgeAnswer:
    topic_id: str
    question: LocalizedText
    answer: LocalizedText
    source: LocalizedText
    score: float


class KnowledgeService:
    def __init__(self, filename: str = "knowledge_base.json") -> None:
        data = load_json(filename)
        self.min_score: float = data.get("min_score", 2)
        sources: dict[str, LocalizedText] = data.get("sources", {})
        self._entries = []
        for e in data["entries"]:
            weights: dict[str, float] = {}
            for keyword, weight in e["keywords"].items():
                # Fold keywords exactly like the farmer's text (diacritics, letter variants, stemming).
                for key in tokens(keyword):
                    weights[key] = max(weights.get(key, 0), weight)
            source = sources.get(e["source"], e["source"]) if isinstance(e["source"], str) else e["source"]
            self._entries.append((e, source, weights))

    def search(self, query: str) -> KnowledgeAnswer | None:
        query_tokens = set(tokens(query, drop_stopwords=True))
        if not query_tokens:
            return None
        best: KnowledgeAnswer | None = None
        for entry, source, weights in self._entries:
            score = sum(w for k, w in weights.items() if k in query_tokens)
            if score >= self.min_score and (best is None or score > best.score):
                best = KnowledgeAnswer(entry["id"], entry["question"], entry["answer"], source, score)
        return best
