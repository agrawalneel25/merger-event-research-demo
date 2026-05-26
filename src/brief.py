from __future__ import annotations

from dataclasses import dataclass

from .retrieval import Passage, Retriever


@dataclass(frozen=True)
class BriefItem:
    label: str
    question: str
    answer: str
    source: Passage


BRIEF_QUERIES = [
    ("Consideration", "What cash consideration will a Northbridge shareholder receive for each share?"),
    ("Outstanding Condition", "Which regulatory clearance remains outstanding and what is the deadline?"),
    ("Long-Stop Date", "What is the long-stop date for the scheme?"),
    ("Financing", "Is completion conditional on financing?"),
]


def build_brief(retriever: Retriever) -> list[BriefItem]:
    items: list[BriefItem] = []
    for label, question in BRIEF_QUERIES:
        hits = retriever.search(question, top_k=1)
        if not hits:
            raise RuntimeError(f"No passage retrieved for {question}")
        passage = hits[0].passage
        items.append(BriefItem(label=label, question=question, answer=passage.text, source=passage))
    return items

