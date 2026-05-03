from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any


class ExperienceItem(BaseModel):
    title: str = ""
    company: str = ""
    period: str = ""
    description: str = ""
    type: str = "Full-time"


class EducationItem(BaseModel):
    degree: str = ""
    institution: str = ""
    period: str = ""
    status: str = "Completed"


class ParsedCV(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []


class EnhanceTextRequest(BaseModel):
    text: str
    tone: str


class EnhanceTextResponse(BaseModel):
    enhanced_text: str


class SuggestSkillsRequest(BaseModel):
    parsed_data: dict


class SuggestSkillsResponse(BaseModel):
    suggested_skills: List[str]


class SaveProfileRequest(BaseModel):
    name: str
    email: str
    final_data: dict


class ProfileResponse(BaseModel):
    id: int
    user_id: int
    final_data: dict

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}
