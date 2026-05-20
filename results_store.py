"""In-memory results store with aggregated statistics."""
import uuid
from datetime import datetime
from collections import Counter
from typing import List


_results: list[dict] = []


def save_result(result: dict) -> dict:
    result["id"] = str(uuid.uuid4())[:8]
    result["created_at"] = datetime.utcnow().isoformat()
    _results.append(result)
    return result


def get_all_results() -> List[dict]:
    return list(reversed(_results))


def get_stats() -> dict:
    if not _results:
        return {"total": 0, "sentiment_counts": {}, "avg_score": 0, "top_topics": [], "top_keywords": []}

    sentiment_counts = Counter(r.get("sentiment", "unknown") for r in _results)
    scores = [r.get("score", 0) for r in _results if isinstance(r.get("score"), (int, float))]
    avg_score = sum(scores) / len(scores) if scores else 0

    all_topics = [t for r in _results for t in r.get("topics", [])]
    all_keywords = [k for r in _results for k in r.get("keywords", [])]

    top_topics = [{"topic": t, "count": c} for t, c in Counter(all_topics).most_common(10)]
    top_keywords = [{"keyword": k, "count": c} for k, c in Counter(all_keywords).most_common(10)]

    return {
        "total": len(_results),
        "sentiment_counts": dict(sentiment_counts),
        "avg_score": round(avg_score, 3),
        "top_topics": top_topics,
        "top_keywords": top_keywords,
    }


def clear_results():
    _results.clear()
