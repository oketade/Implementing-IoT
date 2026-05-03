from fastapi import APIRouter
from pydantic import BaseModel
from schemas import EnhanceTextRequest, EnhanceTextResponse, SuggestSkillsRequest, SuggestSkillsResponse
from services import ai_service

router = APIRouter()


@router.post("/enhance-text", response_model=EnhanceTextResponse)
async def enhance_text(req: EnhanceTextRequest):
    """Enhance a CV text snippet using AI (bio, experience description, etc.)."""
    enhanced = await ai_service.enhance_text_with_ai(req.text, req.tone)
    return EnhanceTextResponse(enhanced_text=enhanced)


@router.post("/suggest-skills", response_model=SuggestSkillsResponse)
async def suggest_skills(req: SuggestSkillsRequest):
    """Suggest skills not already in the parsed CV based on experience context."""
    suggestions = ai_service.suggest_skills(req.parsed_data)
    return SuggestSkillsResponse(suggested_skills=suggestions)


class EnhancePhotoRequest(BaseModel):
    name: str = ""
    current_url: str = ""


class EnhancePhotoResponse(BaseModel):
    enhanced_url: str
    status: str
    mock: bool = True


@router.post("/enhance-photo", response_model=EnhancePhotoResponse)
async def enhance_photo(req: EnhancePhotoRequest):
    """
    AI photo enhancement endpoint.
    Currently returns a polished avatar mock — ready to swap in a real
    image-enhancement API (e.g. Stability AI, Adobe Firefly) when needed.
    """
    initials = "".join(w[0] for w in req.name.split() if w)[:2].upper() or "RD"
    # Mock: return a high-quality generated avatar URL
    enhanced_url = (
        f"https://ui-avatars.com/api/"
        f"?name={initials}"
        f"&background=6affa0&color=080810"
        f"&size=256&bold=true&font-size=0.4&rounded=true"
    )
    return EnhancePhotoResponse(
        enhanced_url=enhanced_url,
        status="enhanced",
        mock=True,
    )
