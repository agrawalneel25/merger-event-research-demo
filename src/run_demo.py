from __future__ import annotations

import argparse
from pathlib import Path

from .brief import BRIEF_QUERIES, build_brief
from .evaluation import evaluate, metrics
from .report import write_report
from .retrieval import Retriever, load_passages


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the synthetic merger-event dashboard.")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "docs" / "index.html", help="HTML report output path."
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help="Call Claude for JSON answers grounded in retrieved passages, printing results to the terminal.",
    )
    parser.add_argument("--model", default="claude-sonnet-4-6", help="Model ID for --claude.")
    args = parser.parse_args()

    passages = load_passages(ROOT / "data" / "documents.csv")
    retriever = Retriever(passages)
    brief = build_brief(retriever)
    evaluations = evaluate(retriever, ROOT / "data" / "evaluation_questions.csv")
    write_report(passages, brief, evaluations, args.output)
    summary = metrics(evaluations)

    print("Merger Event Research Assistant: synthetic document pack")
    print(f"Passages indexed: {len(passages)}")
    print(f"Evaluation queries: {summary['questions']}")
    print(f"Grounded top hits: {summary['grounded_hits']}/{summary['questions']}")
    for item in brief:
        print(f"{item.label}: {item.source.doc_id} / {item.source.section}")
    print(f"Dashboard written to {args.output}")

    if args.claude:
        from .claude import answer_with_citations

        for _, question in BRIEF_QUERIES:
            answer = answer_with_citations(question, retriever.search(question), args.model)
            print(f"\nQuestion: {question}\nClaude answer: {answer}")


if __name__ == "__main__":
    main()

