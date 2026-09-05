import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..services.document_parser import extract_resume_text
from ..services.resume_extractor import extract_resume_data
from ..services.requirement_extractor import extract_hr_requirements
from ..services.matcher import match_resume


router = APIRouter(
    prefix="/api",
    tags=["Resume Analysis"]
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx"
}


@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    requirements: str = Form(...)
):
    """
    Analyze a resume against HR requirements.
    """

    # ========================================================
    # 1. Validate file
    # ========================================================

    if not resume.filename:
        raise HTTPException(
            status_code=400,
            detail="Resume file is required."
        )

    extension = Path(
        resume.filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported resume format. "
                "Only PDF and DOCX are supported."
            )
        )

    # ========================================================
    # 2. Generate unique filename
    # ========================================================

    file_id = uuid.uuid4().hex

    saved_filename = (
        f"{file_id}{extension}"
    )

    file_path = (
        UPLOAD_DIR /
        saved_filename
    )

    # ========================================================
    # 3. Save uploaded file
    # ========================================================

    try:

        with file_path.open("wb") as buffer:

            shutil.copyfileobj(
                resume.file,
                buffer
            )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to save resume."
        ) from exc

    # ========================================================
    # 4. Extract resume text
    # ========================================================

    try:

        resume_text = extract_resume_text(
            str(file_path)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not extract resume text: {exc}"
            )
        ) from exc

    if not resume_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "No text could be extracted "
                "from the resume."
            )
        )

    # ========================================================
    # 5. Extract structured resume data
    # ========================================================

    try:

        resume_data = extract_resume_data(
            resume_text
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Resume AI extraction failed: {exc}"
            )
        ) from exc

    # ========================================================
    # 6. Extract HR requirements
    # ========================================================

    if not requirements.strip():

        raise HTTPException(
            status_code=400,
            detail="HR requirements are required."
        )

    try:

        hr_requirements = (
            extract_hr_requirements(
                requirements
            )
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"HR requirement extraction failed: {exc}"
            )
        ) from exc

    # ========================================================
    # 7. Match resume against requirements
    # ========================================================

    try:

        match_result = match_resume(
            resume_data,
            hr_requirements
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Resume matching failed: {exc}"
            )
        ) from exc

    # ========================================================
    # 8. Return complete result
    # ========================================================

    return {
        "success": True,

        "candidate": resume_data.model_dump(),

        "requirements": (
            hr_requirements.model_dump()
        ),

        "matching": match_result,
    }