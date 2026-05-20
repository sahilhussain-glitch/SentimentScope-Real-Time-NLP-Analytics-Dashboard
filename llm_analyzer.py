"""Core LLM-based sentiment analysis, topic extraction, and keyword extraction."""
import json
from typing import List
from openai import OpenAI
from config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.openai_api_key)

SENTIMENT_CATEGORIES = [
    "positive", "negative", "neutral", "mixed",
    "frustrated", "excited", "confused", "satisfied", "disappointed", "urgent"
]

# ── Prompt Templates with few-shot examples ──────────────────────────────────

CLASSIFY_SYSTEM = """You are a precise sentiment and topic analysis engine for customer feedback.

Analyze the given text and respond ONLY with a valid JSON object — no explanation, no markdown.

Output schema:
{
  "sentiment": "<one of: positive|negative|neutral|mixed|frustrated|excited|confused|satisfied|disappointed|urgent>",
  "confidence": "<high|medium|low>",
  "score": <float -1.0 to 1.0>,
  "topics": ["<topic1>", "<topic2>"],
  "keywords": ["<keyword1>", "<keyword2>", "<keyword3>"],
  "entities": {"product": "<name or null>", "issue": "<issue or null>"},
  "summary": "<1 sentence summary>"
}

Few-shot examples:
Input: "The battery dies after 2 hours. Totally unacceptable for a $500 device."
Output: {"sentiment":"frustrated","confidence":"high","score":-0.85,"topics":["battery life","product quality"],"keywords":["battery","2 hours","unacceptable"],"entities":{"product":"device","issue":"battery life"},"summary":"Customer frustrated about poor battery life on an expensive device."}

Input: "Just received my order and the packaging was beautiful. Product works perfectly!"
Output: {"sentiment":"excited","confidence":"high","score":0.92,"topics":["delivery","packaging","product quality"],"keywords":["packaging","beautiful","works perfectly"],"entities":{"product":null,"issue":null},"summary":"Customer delighted with delivery and product quality."}

Input: "It's okay. Nothing special but does the job."
Output: {"sentiment":"neutral","confidence":"high","score":0.1,"topics":["general experience"],"keywords":["okay","nothing special","does the job"],"entities":{"product":null,"issue":null},"summary":"Customer has a neutral, unremarkable experience with the product."}"""


def analyze_text(text: str) -> dict:
    """
    Analyze a single piece of text for sentiment, topics, keywords.
    Returns a structured dict.
    """
    messages = [
        {"role": "system", "content": CLASSIFY_SYSTEM},
        {"role": "user", "content": f"Analyze this text:\n{text}"},
    ]

    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.1,
        max_tokens=400,
    )

    raw = response.choices[0].message.content.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "sentiment": "neutral",
            "confidence": "low",
            "score": 0.0,
            "topics": [],
            "keywords": [],
            "entities": {"product": None, "issue": None},
            "summary": "Parse error — could not analyze text.",
        }

    result["text"] = text[:200] + ("..." if len(text) > 200 else "")
    result["model"] = settings.chat_model
    return result


def analyze_batch(texts: List[str]) -> List[dict]:
    """Analyze a list of texts. Returns list of analysis dicts."""
    return [analyze_text(t) for t in texts if t.strip()]
