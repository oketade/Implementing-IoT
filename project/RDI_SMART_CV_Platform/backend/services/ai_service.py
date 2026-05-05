import json
import os
import re
from typing import Any


MOCK_ENHANCEMENTS = {
    "professional": "Results-driven professional with strong technical and problem-solving skills.",
    "concise": "Skilled developer with experience building real-world solutions.",
    "confident": "Highly capable and results-driven individual delivering impactful solutions.",
}

CV_JSON_SHAPE = (
    '{"name":"","email":"","phone":"","location":"","summary":"","skills":[],'
    '"experience":[{"title":"","company":"","period":"","description":"","type":""}],'
    '"education":[{"degree":"","institution":"","period":"","status":""}]}'
)


def _mock_enhancement(text: str, tone: str) -> str:
    return MOCK_ENHANCEMENTS.get(tone.lower(), text[:200])


def _log_fallback(provider: str, exc: Exception) -> None:
    print(f"[ai_service] {provider} failed, falling back: {exc.__class__.__name__}: {exc}")


def _openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key.startswith("sk-ant-"):
        return ""
    return key


def _anthropic_key() -> str:
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key

    # Backward-compatible with the current local .env mistake:
    # an Anthropic key was placed under OPENAI_API_KEY.
    misplaced = os.getenv("OPENAI_API_KEY", "").strip()
    if misplaced.startswith("sk-ant-"):
        return misplaced
    return ""


def _extract_json_object(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        data = json.loads(text[start : end + 1])

    if not isinstance(data, dict):
        raise ValueError("AI parser returned non-object JSON")
    return data


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _as_string_list(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        parts = re.split(r"[,;\n]", value)
        return [p.strip() for p in parts if p.strip()]
    if isinstance(value, list):
        out = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("name") or item.get("skill") or item.get("title")
            else:
                text = item
            text = _as_text(text)
            if text:
                out.append(text)
        return out
    return []


def _normalize_items(value: Any, fields: dict[str, str]) -> list[dict[str, str]]:
    if not value:
        return []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []

    normalized = []
    for item in value:
        if isinstance(item, str):
            normalized.append({field: "" for field in fields})
            first_field = next(iter(fields))
            normalized[-1][first_field] = item.strip()
            continue
        if not isinstance(item, dict):
            continue

        row = {}
        for target, default in fields.items():
            row[target] = _as_text(item.get(target, default))
        normalized.append(row)
    return normalized


def _normalize_parsed_cv(data: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "name": _as_text(data.get("name")),
        "email": _as_text(data.get("email")),
        "phone": _as_text(data.get("phone")),
        "location": _as_text(data.get("location")),
        "summary": _as_text(data.get("summary")),
        "skills": _as_string_list(data.get("skills")),
        "experience": _normalize_items(
            data.get("experience"),
            {
                "title": "",
                "company": "",
                "period": "",
                "description": "",
                "type": "",
            },
        ),
        "education": _normalize_items(
            data.get("education"),
            {
                "degree": "",
                "institution": "",
                "period": "",
                "status": "",
            },
        ),
    }

    if not any(
        [
            normalized["name"],
            normalized["email"],
            normalized["skills"],
            normalized["experience"],
            normalized["education"],
        ]
    ):
        raise ValueError("AI parser returned empty CV data")

    return normalized


def _enhance_with_spacy(text: str, tone: str) -> str:
    sentences = [s.strip().capitalize() for s in text.strip().split(".") if s.strip()]
    if not sentences:
        return text

    tone_key = tone.lower()
    if tone_key == "concise":
        return ". ".join(sentences[:2]) + "."
    if tone_key == "professional":
        return "Experienced professional with strong ability to " + sentences[0].lower() + "."
    if tone_key == "confident":
        return "Highly capable individual delivering results. " + ". ".join(sentences) + "."
    return ". ".join(sentences) + "."


async def _enhance_with_openai(text: str, tone: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=_openai_key(), timeout=30)
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    response = await client.chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=400,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional CV writer. Rewrite the text in the requested tone. "
                    "Keep it truthful, specific, recruiter-ready, and concise. Return only the rewritten text."
                ),
            },
            {"role": "user", "content": f"Tone: {tone}\n\nText:\n{text}"},
        ],
    )

    enhanced = response.choices[0].message.content.strip()
    if not enhanced:
        raise ValueError("OpenAI returned empty enhancement")
    return enhanced


async def _parse_with_openai(raw_text: str) -> dict[str, Any]:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=_openai_key(), timeout=45)
    model = os.getenv("OPENAI_MODEL", "gpt-4o")

    response = await client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=1800,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a CV parser. Extract structured information from CV text. "
                    "Return only valid JSON with this exact shape: "
                    f"{CV_JSON_SHAPE}. Use empty strings or empty arrays when data is missing."
                ),
            },
            {"role": "user", "content": raw_text[:20000]},
        ],
    )

    return _normalize_parsed_cv(_extract_json_object(response.choices[0].message.content))


async def _enhance_with_anthropic(text: str, tone: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=_anthropic_key(), timeout=30)
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    msg = client.messages.create(
        model=model,
        max_tokens=400,
        temperature=0.2,
        system=(
            "You are a professional CV writer. Rewrite the text in the requested tone. "
            "Keep it truthful, specific, recruiter-ready, and concise. Return only the rewritten text."
        ),
        messages=[{"role": "user", "content": f"Tone: {tone}\n\nText:\n{text}"}],
    )

    enhanced = msg.content[0].text.strip()
    if not enhanced:
        raise ValueError("Anthropic returned empty enhancement")
    return enhanced


async def _parse_with_anthropic(raw_text: str) -> dict[str, Any]:
    import anthropic

    client = anthropic.Anthropic(api_key=_anthropic_key(), timeout=45)
    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    msg = client.messages.create(
        model=model,
        max_tokens=1800,
        temperature=0,
        system=(
            "You are a CV parser. Extract structured information from CV text. "
            "Return only valid JSON, no markdown and no explanation. "
            f"Use this exact shape: {CV_JSON_SHAPE}. "
            "Use empty strings or empty arrays when data is missing."
        ),
        messages=[{"role": "user", "content": raw_text[:20000]}],
    )

    return _normalize_parsed_cv(_extract_json_object(msg.content[0].text))


async def enhance_text_with_ai(text: str, tone: str) -> str:
    if not text or not text.strip():
        return ""

    if _openai_key():
        try:
            return await _enhance_with_openai(text, tone)
        except Exception as exc:
            _log_fallback("OpenAI enhancement", exc)

    if _anthropic_key():
        try:
            return await _enhance_with_anthropic(text, tone)
        except Exception as exc:
            _log_fallback("Anthropic enhancement", exc)

    try:
        return _enhance_with_spacy(text, tone)
    except Exception as exc:
        _log_fallback("local enhancement", exc)

    return _mock_enhancement(text, tone)


async def parse_cv_with_ai(raw_text: str) -> dict[str, Any]:
    if not raw_text or not raw_text.strip():
        raise ValueError("No text could be extracted from this CV")

    if _openai_key():
        try:
            return await _parse_with_openai(raw_text)
        except Exception as exc:
            _log_fallback("OpenAI CV parsing", exc)

    if _anthropic_key():
        try:
            return await _parse_with_anthropic(raw_text)
        except Exception as exc:
            _log_fallback("Anthropic CV parsing", exc)

    try:
        from services.spacy_parser import parse

        return _normalize_parsed_cv(parse(raw_text))
    except Exception as exc:
        raise ValueError("Parsing failed with API providers and spaCy fallback") from exc


def suggest_skills(parsed_data: dict) -> list[str]:
    existing = {s.lower() for s in parsed_data.get("skills", [])}
    pool = [
        "Docker",
        "REST APIs",
        "PostgreSQL",
        "Git",
        "CI/CD",
        "FastAPI",
        "Azure",
        "Kubernetes",
        "Redis",
        "GraphQL",
        "Linux",
    ]

    return [s for s in pool if s.lower() not in existing][:5]
