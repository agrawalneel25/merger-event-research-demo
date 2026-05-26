from __future__ import annotations

import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "has",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
    "what",
    "which",
    "will",
}


@dataclass(frozen=True)
class Passage:
    doc_id: str
    title: str
    date: str
    section: str
    text: str


@dataclass(frozen=True)
class Hit:
    passage: Passage
    score: float


def load_passages(path: Path) -> list[Passage]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [Passage(**row) for row in csv.DictReader(handle)]


class Retriever:
    def __init__(self, passages: list[Passage]) -> None:
        self.passages = passages
        self.term_counts = [Counter(_tokens(_search_text(passage))) for passage in passages]
        self.idf = _idf(self.term_counts)

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        query_tokens = _tokens(query)
        hits = [
            Hit(passage=passage, score=self._score(index, query_tokens))
            for index, passage in enumerate(self.passages)
        ]
        ranked = sorted(hits, key=lambda hit: (-hit.score, hit.passage.date, hit.passage.doc_id))
        return [hit for hit in ranked[:top_k] if hit.score > 0]

    def _score(self, index: int, query_tokens: list[str]) -> float:
        counts = self.term_counts[index]
        score = sum(self.idf.get(token, 0.0) * counts.get(token, 0) for token in query_tokens)
        phrase = " ".join(query_tokens)
        if phrase and phrase in _search_text(self.passages[index]).lower():
            score += 4.0
        return score


def _tokens(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOP_WORDS]


def _search_text(passage: Passage) -> str:
    return f"{passage.title} {passage.section} {passage.text}"


def _idf(counts: list[Counter[str]]) -> dict[str, float]:
    terms = {term for counter in counts for term in counter}
    total = len(counts)
    return {
        term: math.log((total + 1) / (1 + sum(term in counter for counter in counts))) + 1
        for term in terms
    }

