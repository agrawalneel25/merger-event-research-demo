from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request

from .retrieval import Hit


API_URL = "https://api.anthropic.com/v1/messages"


def answer_with_citations(question: str, hits: list[Hit], model: str) -> dict[str, object]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY to use --claude.")
    evidence = [
        {"source_id": hit.passage.doc_id, "section": hit.passage.section, "text": hit.passage.text}
        for hit in hits
    ]
    prompt = (
        "Answer a research question using only the supplied synthetic merger-document evidence. "
        "Return only JSON with keys answer, citations and insufficient_evidence. "
        "citations must be a list of source_id values used. Do not recommend a trade, estimate spread, "
        "or use facts outside the evidence. If evidence is missing, say so. Question: "
        + question
        + " Evidence: "
        + json.dumps(evidence)
    )
    body = json.dumps(
        {
            "model": model,
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Claude request failed: {exc.code} {detail}") from exc
    return _extract_json(_response_text(result))


def _response_text(result: dict) -> str:
    text = [
        str(block.get("text", ""))
        for block in result.get("content", [])
        if isinstance(block, dict) and block.get("type") == "text"
    ]
    if not text:
        raise RuntimeError("Claude response did not contain text.")
    return "\n".join(text)


def _extract_json(text: str) -> dict[str, object]:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match is None:
            raise RuntimeError("Could not parse Claude answer as JSON.")
        result = json.loads(match.group(0))
    if not isinstance(result, dict):
        raise RuntimeError("Claude answer was not a JSON object.")
    return result

