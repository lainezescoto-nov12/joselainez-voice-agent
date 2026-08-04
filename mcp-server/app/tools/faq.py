"""dealership_faq_lookup — grounded in a small static KB.

Keyword overlap scoring, not embeddings: the KB is a handful of entries, and
a real vector-search KB is explicitly deferred (see architecture spec).
Swap the scoring function for an embedding lookup without changing the tool
signature when the KB grows.
"""
from app import config
from app.data.mock_inventory import FAQ_KB


def _score(query_words: set[str], entry: dict) -> int:
    entry_words = set((entry["question"] + " " + entry["answer"]).lower().split())
    return len(query_words & entry_words)


def dealership_faq_lookup(question: str, tenant_id: str = config.DEFAULT_TENANT_ID) -> dict:
    """Answer a general dealership question from the knowledge base."""
    query_words = set(question.lower().split())
    scored = sorted(FAQ_KB, key=lambda e: _score(query_words, e), reverse=True)
    best = scored[0]

    if _score(query_words, best) == 0:
        return {
            "found": False,
            "answer": "I don't have that in the knowledge base — let me connect you with a team member.",
        }

    return {"found": True, "matched_question": best["question"], "answer": best["answer"]}
