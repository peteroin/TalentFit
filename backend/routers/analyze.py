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

    The uploaded resume is stored temporarily,
    processed, and deleted after the analysis.
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
    # 2. Validate HR requirements
    # ========================================================

    if not requirements.strip():
        raise HTTPException(
            status_code=400,
            detail="HR requirements are required."
        )

    # ========================================================
    # 3. Generate unique temporary filename
    # ========================================================

    file_id = uuid.uuid4().hex

    saved_filename = (
        f"{file_id}{extension}"
    )

    file_path = (
        UPLOAD_DIR /
        saved_filename
    )

    try:

        # ====================================================
        # 4. Save uploaded file temporarily
        # ====================================================

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

        # ====================================================
        # 5. Extract resume text
        # ====================================================

        try:

            resume_text = extract_resume_text(
                str(file_path)
            )

        except Exception as exc:

            raise HTTPException(
                status_code=400,
                detail="Could not extract resume text."
            ) from exc

        if not resume_text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "No text could be extracted "
                    "from the resume."
                )
            )

        # ====================================================
        # 6. Extract structured resume data
        # ====================================================

        try:

            resume_data = extract_resume_data(
                resume_text
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail="Resume AI extraction failed."
            ) from exc

        # ====================================================
        # 7. Extract HR requirements
        # ====================================================

        try:

            hr_requirements = (
                extract_hr_requirements(
                    requirements
                )
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail="HR requirement extraction failed."
            ) from exc

        # ====================================================
        # 8. Match resume against requirements
        # ====================================================

        try:

            match_result = match_resume(
                resume_data,
                hr_requirements
            )

        except Exception as exc:

            raise HTTPException(
                status_code=500,
                detail="Resume matching failed."
            ) from exc

        # ====================================================
        # 9. Return complete result
        # ====================================================

        return {
            "success": True,

            "candidate": (
                resume_data.model_dump()
            ),

            "requirements": (
                hr_requirements.model_dump()
            ),

            "matching": match_result,
        }

    finally:

        # ====================================================
        # 10. Delete temporary resume
        # ====================================================

        try:

            if file_path.exists():
                file_path.unlink()

        except Exception:

            # Do not hide the actual analysis result
            # if cleanup happens to fail.
            pass

        await resume.close()