from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Body
from sqlalchemy.orm import Session
from database import get_db
from models import CV, User
from schemas import ParsedCV
from services import cv_parser, ai_service

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}


def _get_or_create_default_user(db: Session) -> User:
    user = db.query(User).filter(User.email == "peter.oketade@student.fi").first()
    if not user:
        user = User(name="Peter Adedayo Oketade", email="peter.oketade@student.fi")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.post("/upload-cv", response_model=ParsedCV)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a CV file (PDF/DOCX/TXT), extract text, parse with AI."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.lower().rsplit(".", 1)[-1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '.{ext}'. Allowed: PDF, DOCX, TXT",
        )

    try:
        file_bytes = await file.read()
        raw_text = cv_parser.extract_text(file.filename, file_bytes)
        parsed = await ai_service.parse_cv_with_ai(raw_text)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # Persist to DB — don't let a dropped connection block the response
    try:
        user = _get_or_create_default_user(db)
        db_cv = CV(user_id=user.id, raw_text=raw_text, parsed_json=parsed)
        db.add(db_cv)
        db.commit()
    except Exception:
        pass

    return parsed


@router.post("/parse-cv", response_model=ParsedCV)
async def parse_cv_text(raw_text: str = Body(..., embed=True)):
    """Parse CV from raw text string (e.g., pasted content)."""
    parsed = await ai_service.parse_cv_with_ai(raw_text)
    return parsed
