# import os
# import json

# # ──────────────────────────────────────────────────────────────
# # Mock enhancement text for each tone (fallback when no API key)
# # ──────────────────────────────────────────────────────────────
# MOCK_ENHANCEMENTS = {
#     "professional": (
#         "Results-driven Industrial Information Technology student with demonstrated expertise in "
#         "IoT systems architecture, embedded programming, and full-stack platform development. "
#         "Proven track record of delivering scalable, data-driven applications that bridge "
#         "engineering principles with practical industry solutions."
#     ),
#     "concise": (
#         "Industrial IT student specializing in IoT, embedded systems, and full-stack development. "
#         "Builds data-driven applications that solve real industry problems."
#     ),
#     "confident": (
#         "Ambitious Industrial IT student dominating the IoT and embedded systems space. "
#         "Building cutting-edge platforms that transform raw sensor data into actionable "
#         "industry intelligence — ready to lead the next wave of industrial digitalization."
#     ),
#     "story-driven": (
#         "My journey in Industrial Information Technology began with a fascination for how physical "
#         "systems communicate with digital platforms. Today, I channel that curiosity into building "
#         "IoT solutions and data-driven applications that solve real problems for real industries."
#     ),
#     "impact-focused": (
#         "Engineered and deployed backend microservices that reduced internal tool response times by 40%. "
#         "Led REST API integrations serving 500+ daily active users, collaborating with senior engineers "
#         "to maintain 99.9% service uptime across the internship period."
#     ),
#     "technical": (
#         "Architected RESTful microservices using Node.js and FastAPI with PostgreSQL persistence. "
#         "Implemented OAuth2 authentication, Redis caching layers, and full ORM patterns. "
#         "Maintained CI/CD pipelines with Docker containerization and GitHub Actions automation."
#     ),
#     "technical depth": (
#         "Architected RESTful microservices using Node.js and FastAPI with PostgreSQL persistence. "
#         "Implemented OAuth2 authentication, Redis caching layers, and full ORM patterns. "
#         "Maintained CI/CD pipelines with Docker containerization and GitHub Actions automation."
#     ),
#     "concise bullet": (
#         "• Built backend microservices for internal tooling infrastructure\n"
#         "• Integrated REST APIs with senior engineering team support\n"
#         "• Maintained 99.9% service uptime throughout full internship"
#     ),
# }


# def _mock_enhancement(text: str, tone: str) -> str:
#     key = tone.lower()
#     return MOCK_ENHANCEMENTS.get(key, f"[Enhanced — {tone}]\n\n{text[:300]}")


# # ──────────────────────────────────────────────────────────────
# # Public API
# # ──────────────────────────────────────────────────────────────

# async def enhance_text_with_ai(text: str, tone: str) -> str:
#     if os.getenv("ANTHROPIC_API_KEY"):
#         return await _enhance_with_anthropic(text, tone)
#     if os.getenv("OPENAI_API_KEY"):
#         return await _enhance_with_openai(text, tone)
#     return _mock_enhancement(text, tone)


# async def parse_cv_with_ai(raw_text: str) -> dict:
#     if not raw_text.strip():
#         raise ValueError(
#             "No text could be extracted from this file. "
#             "If it is a scanned PDF, please export your CV as .docx or .txt and upload that instead."
#         )

#     if os.getenv("ANTHROPIC_API_KEY"):
#         return await _parse_with_anthropic(raw_text)
#     if os.getenv("OPENAI_API_KEY"):
#         return await _parse_with_openai(raw_text)

#     # Free local fallback — no API key required
#     try:
#         from services.spacy_parser import parse as spacy_parse
#         return spacy_parse(raw_text)
#     except Exception:
#         pass

#     raise ValueError(
#         "Parsing failed. Install spaCy (pip install spacy && python -m spacy download en_core_web_sm) "
#         "or set ANTHROPIC_API_KEY in backend/.env."
#     )


# def suggest_skills(parsed_data: dict) -> list:
#     existing = {s.lower() for s in parsed_data.get("skills", [])}
#     pool = [
#         "Docker", "REST APIs", "PostgreSQL", "Git", "Agile / Scrum",
#         "CI/CD", "TypeScript", "FastAPI", "Azure", "Kubernetes",
#         "Redis", "GraphQL", "Linux", "Terraform",
#     ]
#     return [s for s in pool if s.lower() not in existing][:6]


# # ──────────────────────────────────────────────────────────────
# # Anthropic helpers
# # ──────────────────────────────────────────────────────────────

# async def _enhance_with_anthropic(text: str, tone: str) -> str:
#     try:
#         import anthropic

#         client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#         word_count = len(text.split())
#         is_exp = word_count < 80

#         if is_exp:
#             system = (
#                 f'You are a professional CV writer. Rewrite the experience description '
#                 f'below in a "{tone}" style. 2–3 sentences max. Strong, specific, '
#                 f'recruiter-ready. Return ONLY the rewritten text.'
#             )
#         else:
#             system = (
#                 f'You are a professional CV writer. Rewrite the profile summary below '
#                 f'in a "{tone}" style. 2–4 sentences. Compelling and authentic. '
#                 f'Return ONLY the rewritten text.'
#             )

#         message = client.messages.create(
#             model="claude-sonnet-4-6",
#             max_tokens=400,
#             system=system,
#             messages=[{"role": "user", "content": text}],
#         )
#         return message.content[0].text.strip()
#     except Exception:
#         return _mock_enhancement(text, tone)


# async def _parse_with_anthropic(raw_text: str) -> dict:
#     try:
#         import anthropic

#         client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
#         system = (
#             "You are a CV parser. Extract structured information from the CV text below. "
#             "Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):\n"
#             '{"name":"","email":"","phone":"","location":"","summary":"",'
#             '"skills":[],'
#             '"experience":[{"title":"","company":"","period":"","description":"","type":""}],'
#             '"education":[{"degree":"","institution":"","period":"","status":""}]}'
#         )
#         message = client.messages.create(
#             model="claude-sonnet-4-6",
#             max_tokens=1500,
#             system=system,
#             messages=[{"role": "user", "content": raw_text}],
#         )
#         return json.loads(message.content[0].text.strip())
#     except Exception:
#         from services.spacy_parser import parse as spacy_parse
#         return spacy_parse(raw_text)


# # ──────────────────────────────────────────────────────────────
# # OpenAI helpers
# # ──────────────────────────────────────────────────────────────

# async def _enhance_with_openai(text: str, tone: str) -> str:
#     try:
#         from openai import AsyncOpenAI

#         client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#         response = await client.chat.completions.create(
#             model="gpt-4o",
#             max_tokens=400,
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         f"You are a professional CV writer. Rewrite the text in a '{tone}' style. "
#                         "Return ONLY the rewritten text, no explanation."
#                     ),
#                 },
#                 {"role": "user", "content": text},
#             ],
#         )
#         return response.choices[0].message.content.strip()
#     except Exception:
#         return _mock_enhancement(text, tone)


# async def _parse_with_openai(raw_text: str) -> dict:
#     try:
#         from openai import AsyncOpenAI

#         client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#         response = await client.chat.completions.create(
#             model="gpt-4o",
#             max_tokens=1500,
#             response_format={"type": "json_object"},
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                         "You are a CV parser. Extract structured information and return JSON with keys: "
#                         "name, email, phone, location, summary, skills (array of strings), "
#                         "experience (array of {title, company, period, description, type}), "
#                         "education (array of {degree, institution, period, status})"
#                     ),
#                 },
#                 {"role": "user", "content": raw_text},
#             ],
#         )
#         return json.loads(response.choices[0].message.content)
#     except Exception:
#         from services.spacy_parser import parse as spacy_parse
#         return spacy_parse(raw_text)
# # ─────────────────────────────────────────────
# # PUBLIC API (REQUIRED)
# # ─────────────────────────────────────────────

# async def parse_cv_with_ai(raw_text: str) -> dict:
#     if not raw_text.strip():
#         raise ValueError(
#             "No text could be extracted from this file."
#         )

#     if os.getenv("ANTHROPIC_API_KEY"):
#         return await _parse_with_anthropic(raw_text)

#     if os.getenv("OPENAI_API_KEY"):
#         return await _parse_with_openai(raw_text)

#     # fallback
#     try:
#         from services.spacy_parser import parse as spacy_parse
#         return spacy_parse(raw_text)
#     except Exception:
#         raise ValueError("Parsing failed — no AI key or spaCy available.")


# async def enhance_text_with_ai(text: str, tone: str) -> str:
#     if os.getenv("ANTHROPIC_API_KEY"):
#         return await _enhance_with_anthropic(text, tone)

#     if os.getenv("OPENAI_API_KEY"):
#         return await _enhance_with_openai(text, tone)

#     return text

import os
import json

# ─────────────────────────────────────────────
# MOCK FALLBACKS (used if everything fails)
# ─────────────────────────────────────────────
MOCK_ENHANCEMENTS = {
    "professional": "Results-driven professional with strong technical and problem-solving skills.",
    "concise": "Skilled developer with experience building real-world solutions.",
    "confident": "Highly capable and results-driven individual delivering impactful solutions.",
}


def _mock_enhancement(text: str, tone: str) -> str:
    return MOCK_ENHANCEMENTS.get(tone.lower(), text[:200])


# ─────────────────────────────────────────────
# SIMPLE LOCAL FALLBACK (spaCy-style rewrite)
# ─────────────────────────────────────────────
def _enhance_with_spacy(text: str, tone: str) -> str:
    sentences = text.strip().split(".")
    sentences = [s.strip().capitalize() for s in sentences if s.strip()]

    if not sentences:
        return text

    if tone.lower() == "concise":
        return ". ".join(sentences[:2]) + "."

    if tone.lower() == "professional":
        return "Experienced professional with strong ability to " + sentences[0].lower() + "."

    if tone.lower() == "confident":
        return "Highly capable individual delivering results. " + ". ".join(sentences) + "."

    return ". ".join(sentences) + "."


# ─────────────────────────────────────────────
# OPENAI
# ─────────────────────────────────────────────
async def _enhance_with_openai(text: str, tone: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": f"Rewrite the text in a '{tone}' CV style. Return only the text."
            },
            {"role": "user", "content": text},
        ],
    )

    return response.choices[0].message.content.strip()


async def _parse_with_openai(raw_text: str) -> dict:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = await client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Extract CV data into JSON: name, email, phone, location, summary, skills, experience, education."
            },
            {"role": "user", "content": raw_text},
        ],
    )

    return json.loads(response.choices[0].message.content)


# ─────────────────────────────────────────────
# ANTHROPIC
# ─────────────────────────────────────────────
async def _enhance_with_anthropic(text: str, tone: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": f"Rewrite in {tone} tone:\n{text}"}],
    )

    return msg.content[0].text.strip()


async def _parse_with_anthropic(raw_text: str) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": raw_text}],
    )

    return json.loads(msg.content[0].text.strip())


# ─────────────────────────────────────────────
# PUBLIC API (FINAL)
# ─────────────────────────────────────────────
async def enhance_text_with_ai(text: str, tone: str) -> str:
    if not text or not text.strip():
        return ""

    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            return await _enhance_with_openai(text, tone)
        except Exception:
            pass

    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return await _enhance_with_anthropic(text, tone)
        except Exception:
            pass

    # Local fallback
    try:
        return _enhance_with_spacy(text, tone)
    except Exception:
        pass

    return _mock_enhancement(text, tone)


async def parse_cv_with_ai(raw_text: str) -> dict:
    if not raw_text.strip():
        raise ValueError("No text provided")

    # OpenAI
    if os.getenv("OPENAI_API_KEY"):
        try:
            return await _parse_with_openai(raw_text)
        except Exception:
            pass

    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            return await _parse_with_anthropic(raw_text)
        except Exception:
            pass

    # spaCy fallback
    try:
        from services.spacy_parser import parse
        return parse(raw_text)
    except Exception:
        raise ValueError("Parsing failed (no AI + no spaCy)")


def suggest_skills(parsed_data: dict) -> list:
    existing = {s.lower() for s in parsed_data.get("skills", [])}

    pool = [
        "Docker", "REST APIs", "PostgreSQL", "Git",
        "CI/CD", "FastAPI", "Azure", "Kubernetes",
        "Redis", "GraphQL", "Linux"
    ]

    return [s for s in pool if s.lower() not in existing][:5]