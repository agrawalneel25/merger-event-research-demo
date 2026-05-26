from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .retrieval import Hit, Retriever


@dataclass(frozen=True)
class EvaluationResult:
    question: str
    expected_doc_id: str
    hit: Hit | None
    source_correct: bool
    terms_present: bool


def evaluate(retriever: Retriever, questions_path: Path) -> list[EvaluationResult]:
    results: list[EvaluationResult] = []
    with questions_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            hits = retriever.search(row["question"], top_k=1)
            hit = hits[0] if hits else None
            required_terms = row["required_terms"].lower().split("|")
            text = hit.passage.text.lower() if hit else ""
            results.append(
                EvaluationResult(
                    question=row["question"],
                    expected_doc_id=row["expected_doc_id"],
                    hit=hit,
                    source_correct=bool(hit and hit.passage.doc_id == row["expected_doc_id"]),
                    terms_present=all(term in text for term in required_terms),
                )
            )
    return results


def metrics(results: list[EvaluationResult]) -> dict[str, int]:
    return {
        "questions": len(results),
        "source_hits": sum(result.source_correct for result in results),
        "grounded_hits": sum(result.source_correct and result.terms_present for result in results),
    }

