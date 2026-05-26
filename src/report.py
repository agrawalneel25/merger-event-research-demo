from __future__ import annotations

from html import escape
from pathlib import Path

from .brief import BriefItem
from .evaluation import EvaluationResult, metrics
from .retrieval import Passage


def write_report(
    passages: list[Passage],
    brief: list[BriefItem],
    evaluations: list[EvaluationResult],
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_report(passages, brief, evaluations), encoding="utf-8")


def render_report(
    passages: list[Passage], brief: list[BriefItem], evaluations: list[EvaluationResult]
) -> str:
    result_metrics = metrics(evaluations)
    brief_cards = "\n".join(_brief_card(item) for item in brief)
    doc_rows = "\n".join(_document_row(passage) for passage in passages)
    eval_rows = "\n".join(_evaluation_row(result) for result in evaluations)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Merger Event Research Assistant</title>
  <style>
    :root {{
      --navy: #101b30;
      --blue: #365e91;
      --paper: #f6f5f2;
      --surface: #ffffff;
      --ink: #192438;
      --muted: #667287;
      --border: #e0dfdc;
      --green: #17724e;
      --green-bg: #daf0e6;
      --gold: #b48231;
      --gold-bg: #f6ecd7;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--paper); color: var(--ink); font-family: Arial, Helvetica, sans-serif; }}
    header {{ background: var(--navy); color: white; padding: 42px max(24px, calc((100% - 1160px) / 2)); }}
    .tag {{ color: #94bce7; font-size: 12px; font-weight: bold; letter-spacing: .16em; text-transform: uppercase; }}
    h1 {{ font-size: clamp(32px, 5vw, 48px); margin: 11px 0 13px; }}
    header p {{ color: #d6deea; line-height: 1.55; margin: 0; max-width: 780px; }}
    main {{ max-width: 1160px; margin: 0 auto; padding: 26px 24px 48px; }}
    .notice {{ background: var(--gold-bg); border-radius: 12px; color: #59441b; margin-bottom: 22px; padding: 14px 18px; font-size: 14px; }}
    .metrics {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 26px; }}
    .metric, .panel, .card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 15px; }}
    .metric {{ padding: 17px; }}
    .metric span {{ color: var(--muted); display: block; font-size: 13px; margin-bottom: 8px; }}
    .metric strong {{ font-size: 29px; }}
    h2 {{ font-size: 20px; margin: 0 0 15px; }}
    .cards {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 27px; }}
    .card {{ padding: 19px; }}
    .card h3 {{ color: var(--blue); font-size: 14px; letter-spacing: .06em; margin: 0 0 10px; text-transform: uppercase; }}
    .answer {{ font-size: 14px; line-height: 1.55; margin: 0 0 12px; }}
    .source {{ color: var(--muted); font-size: 12px; }}
    .panel {{ margin-bottom: 25px; overflow: hidden; padding: 20px; }}
    table {{ border-collapse: collapse; font-size: 14px; width: 100%; }}
    th {{ border-bottom: 1px solid var(--border); color: var(--muted); font-size: 12px; padding: 10px 8px; text-align: left; text-transform: uppercase; }}
    td {{ border-bottom: 1px solid #eeece8; line-height: 1.45; padding: 11px 8px; vertical-align: top; }}
    tr:last-child td {{ border-bottom: none; }}
    .pass {{ background: var(--green-bg); border-radius: 20px; color: var(--green); font-size: 12px; font-weight: bold; padding: 5px 10px; }}
    code {{ background: #eef1f4; border-radius: 4px; font-size: 12px; padding: 2px 5px; }}
    footer {{ color: var(--muted); font-size: 13px; line-height: 1.55; }}
    @media (max-width: 820px) {{ .metrics, .cards {{ grid-template-columns: repeat(2, 1fr); }} .panel {{ overflow-x: auto; }} }}
    @media (max-width: 540px) {{ .metrics, .cards {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <header>
    <div class="tag">Illustrative event-driven research prototype</div>
    <h1>Merger Event Research Assistant</h1>
    <p>A retrieval-grounded review screen for an announced acquisition: key terms, outstanding conditions, dated evidence and a small evaluation set.</p>
  </header>
  <main>
    <div class="notice"><strong>Synthetic document pack only.</strong> This dashboard is not investment advice, does not use Jerpoint data and does not recommend a position.</div>
    <section class="metrics">
      <div class="metric"><span>Transaction</span><strong>Helix / Northbridge</strong></div>
      <div class="metric"><span>Source passages</span><strong>{len(passages)}</strong></div>
      <div class="metric"><span>Evaluation queries</span><strong>{result_metrics["questions"]}</strong></div>
      <div class="metric"><span>Grounded top hits</span><strong>{result_metrics["grounded_hits"]}/{result_metrics["questions"]}</strong></div>
    </section>
    <section>
      <h2>Transaction brief with cited evidence</h2>
      <div class="cards">{brief_cards}</div>
    </section>
    <section class="panel">
      <h2>Retrieval evaluation</h2>
      <table>
        <thead><tr><th>Question</th><th>Top retrieved source</th><th>Check</th></tr></thead>
        <tbody>{eval_rows}</tbody>
      </table>
    </section>
    <section class="panel">
      <h2>Synthetic source pack</h2>
      <table>
        <thead><tr><th>Date</th><th>Document</th><th>Section</th><th>Passage</th></tr></thead>
        <tbody>{doc_rows}</tbody>
      </table>
    </section>
    <footer>
      Method: deterministic token-based retrieval ranks synthetic document passages for each diligence question. The default brief displays retrieved evidence directly. An optional Claude route can generate a cited answer from retrieved passages only and is instructed not to recommend a trade.
    </footer>
  </main>
</body>
</html>
"""


def _brief_card(item: BriefItem) -> str:
    return (
        '<article class="card">'
        f"<h3>{escape(item.label)}</h3>"
        f'<p class="answer">{escape(item.answer)}</p>'
        f'<div class="source">Source: <code>{escape(item.source.doc_id)}</code>, '
        f"{escape(item.source.section)}, {escape(item.source.date)}</div>"
        "</article>"
    )


def _evaluation_row(result: EvaluationResult) -> str:
    hit = result.hit.passage if result.hit else None
    source = f"{hit.doc_id} / {hit.section}" if hit else "No hit"
    passed = result.source_correct and result.terms_present
    badge = '<span class="pass">Pass</span>' if passed else "Review"
    return f"<tr><td>{escape(result.question)}</td><td><code>{escape(source)}</code></td><td>{badge}</td></tr>"


def _document_row(passage: Passage) -> str:
    return (
        "<tr>"
        f"<td>{escape(passage.date)}</td>"
        f"<td>{escape(passage.title)}</td>"
        f"<td>{escape(passage.section)}</td>"
        f"<td>{escape(passage.text)}</td>"
        "</tr>"
    )

