from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from src.brief import build_brief
from src.claude import answer_with_citations
from src.evaluation import evaluate, metrics
from src.report import render_report
from src.retrieval import Retriever, load_passages


ROOT = Path(__file__).resolve().parents[1]


class MergerEventDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.passages = load_passages(ROOT / "data" / "documents.csv")
        self.retriever = Retriever(self.passages)

    def test_evaluation_queries_retrieve_grounded_source(self) -> None:
        results = evaluate(self.retriever, ROOT / "data" / "evaluation_questions.csv")
        summary = metrics(results)
        self.assertEqual(summary["questions"], 4)
        self.assertEqual(summary["source_hits"], 4)
        self.assertEqual(summary["grounded_hits"], 4)

    def test_brief_contains_key_transaction_sources(self) -> None:
        brief = {item.label: item.source.doc_id for item in build_brief(self.retriever)}
        self.assertEqual(brief["Consideration"], "offer_announcement")
        self.assertEqual(brief["Outstanding Condition"], "regulatory_update")
        self.assertEqual(brief["Long-Stop Date"], "scheme_document")
        self.assertEqual(brief["Financing"], "financing_confirmation")

    def test_report_labels_synthetic_scope_and_no_advice(self) -> None:
        results = evaluate(self.retriever, ROOT / "data" / "evaluation_questions.csv")
        html = render_report(self.passages, build_brief(self.retriever), results)
        self.assertIn("Synthetic document pack only", html)
        self.assertIn("not investment advice", html)
        self.assertIn("4/4", html)

    @patch.dict("os.environ", {}, clear=True)
    def test_claude_option_requires_key(self) -> None:
        with self.assertRaises(RuntimeError):
            answer_with_citations("What is the consideration?", self.retriever.search("consideration"), "claude-sonnet-4-6")


if __name__ == "__main__":
    unittest.main()

