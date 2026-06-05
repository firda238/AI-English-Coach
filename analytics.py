"""Learning analytics over saved practice records."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

from storage import load_practice_record


def load_records(files: Iterable[Path]) -> List[Dict]:
    """Load valid practice records and skip malformed files."""
    records = []
    for file in files:
        try:
            record = load_practice_record(file)
            record["_file_name"] = file.name
            record["_path"] = str(file)
            records.append(record)
        except Exception:
            continue
    return records


def filter_records(records: List[Dict], scenario: str = "全部") -> List[Dict]:
    """Filter records by scenario label."""
    if scenario == "全部":
        return records
    return [record for record in records if record.get("scenario") == scenario]


def summarize_records(records: List[Dict]) -> Dict:
    """Return aggregate learning statistics."""
    total = len(records)
    scores = [
        record.get("overall_score", record.get("score_result", {}).get("total_score"))
        for record in records
        if isinstance(record.get("overall_score", record.get("score_result", {}).get("total_score")), int)
    ]
    scenario_counts = Counter(record.get("scenario", "未知") for record in records)
    summaries = sum(1 for record in records if record.get("lesson_summary"))
    return {
        "total_records": total,
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "best_score": max(scores) if scores else 0,
        "summary_count": summaries,
        "scenario_counts": dict(scenario_counts),
    }


def score_trend(records: List[Dict]) -> List[Dict]:
    """Return score trend data sorted by time."""
    rows = []
    for record in sorted(records, key=lambda item: item.get("time", "")):
        score = record.get("overall_score", record.get("score_result", {}).get("total_score"))
        if isinstance(score, int):
            rows.append(
                {
                    "time": record.get("time", ""),
                    "scenario": record.get("scenario", "未知"),
                    "score": score,
                }
            )
    return rows


def dimension_averages(records: List[Dict]) -> Dict[str, float]:
    """Return average score for each scoring dimension."""
    buckets: Dict[str, List[int]] = defaultdict(list)
    for record in records:
        score_items = record.get("score_history") or [record.get("score_result", {})]
        for score_item in score_items:
            dimensions = score_item.get("dimensions", {})
            for key, item in dimensions.items():
                score = item.get("score")
                if isinstance(score, int):
                    buckets[key].append(score)
    return {key: round(sum(values) / len(values), 1) for key, values in buckets.items() if values}


def error_frequency(records: List[Dict]) -> Dict[str, int]:
    """Return frequency of feedback issue explanations."""
    counter: Counter[str] = Counter()
    for record in records:
        feedback_items = record.get("feedback_history") or [record.get("correction_feedback", {})]
        for feedback in feedback_items:
            issues = feedback.get("issue_explanation", [])
            for issue in issues:
                counter[issue] += 1
    return dict(counter.most_common(8))
