from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from models import Profile, User
from schemas import SaveProfileRequest, ProfileResponse
from services import pdf_generator

router = APIRouter()


@router.post("/save-profile", response_model=ProfileResponse)
async def save_profile(req: SaveProfileRequest, db: Session = Depends(get_db)):
    """Create or update a user profile in the database."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        user = User(name=req.name, email=req.email)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.name = req.name
        db.commit()

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile:
        profile.final_data = req.final_data
    else:
        profile = Profile(user_id=user.id, final_data=req.final_data)
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profile/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Fetch a profile by its numeric ID."""
    profile = db.query(Profile).filter(Profile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/profile/by-email/{email}", response_model=ProfileResponse)
async def get_profile_by_email(email: str, db: Session = Depends(get_db)):
    """Fetch a profile by user email."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/generate-pdf")
async def generate_pdf(
    profile_data: dict,
    template: str = "Classic",
):
    """Generate and stream a PDF of the CV."""
    pdf_bytes = pdf_generator.generate_cv_pdf(profile_data, template)

    # Detect if WeasyPrint produced a real PDF
    is_pdf = pdf_bytes[:4] == b"%PDF"
    media_type = "application/pdf" if is_pdf else "text/html"
    filename_ext = "pdf" if is_pdf else "html"

    safe_name = profile_data.get("name", "cv").replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}_cv.{filename_ext}"'
        },
    )
