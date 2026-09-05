import re
from datetime import datetime
from difflib import SequenceMatcher

from ..models.hr_schemas import HRRequirements
from ..models.schemas import ResumeData


MATCH_THRESHOLD = 90
PARTIAL_THRESHOLD = 60

WEIGHTS = {
    "skills": 0.35,
    "experience": 0.30,
    "projects": 0.20,
    "education": 0.10,
    "certifications": 0.05,
}


# ============================================================
# NORMALIZATION
# ============================================================

def normalize(text: str) -> str:
    if not text:
        return ""

    text = text.lower().strip()

    replacements = {
        "github": "git",
        "github actions": "git",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "large language models": "llm",
        "large language model": "llm",
        "artificial intelligence": "ai",
        "restful api": "rest api",
        "restful apis": "rest apis",
        "apis": "api",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[^a-z0-9+#.\-/ ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def similarity(a: str, b: str) -> float:
    a = normalize(a)
    b = normalize(b)

    if not a or not b:
        return 0.0

    if a == b:
        return 100.0

    if a in b or b in a:
        return 92.0

    return SequenceMatcher(None, a, b).ratio() * 100


# ============================================================
# CONCEPT MATCHING
# ============================================================

CONCEPTS = {
    "machine learning": [
        "machine learning",
        "ml",
        "scikit learn",
        "sklearn",
        "predictive modeling",
        "classification",
        "regression",
    ],
    "ai": [
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "neural network",
        "cnn",
        "computer vision",
    ],
    "llm": [
        "llm",
        "large language model",
        "large language models",
        "generative ai",
        "genai",
        "language model",
    ],
    "backend": [
        "backend",
        "back end",
        "server side",
        "api development",
        "rest api",
        "rest apis",
        "fastapi",
        "django",
        "flask",
        "node.js",
        "nodejs",
        "express",
    ],
    "computer science": [
        "computer science",
        "computer engineering",
        "software engineering",
        "information technology",
        "information systems",
    ],
}


def concept_match_score(requirement: str, candidate_text: str) -> float:
    requirement_norm = normalize(requirement)
    candidate_norm = normalize(candidate_text)

    if not requirement_norm or not candidate_norm:
        return 0.0

    direct_score = similarity(requirement_norm, candidate_norm)

    if direct_score >= MATCH_THRESHOLD:
        return direct_score

    for concept, keywords in CONCEPTS.items():
        requirement_has_concept = any(
            normalize(keyword) in requirement_norm
            for keyword in keywords
        )

        if requirement_has_concept:
            candidate_has_concept = any(
                normalize(keyword) in candidate_norm
                for keyword in keywords
            )

            if candidate_has_concept:
                return 90.0

    return direct_score


# ============================================================
# SKILL MATCHING
# ============================================================

def match_skills(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    candidate_skills = resume.skills

    matched = []
    partial = []
    missing = []

    all_requirements = []

    for skill in requirements.required_skills:
        all_requirements.append((skill, True))

    for skill in requirements.preferred_skills:
        all_requirements.append((skill, False))

    scores = []

    for requirement, required in all_requirements:

        best_score = 0.0
        best_match = None

        for candidate_skill in candidate_skills:
            score = similarity(requirement, candidate_skill)

            if score > best_score:
                best_score = score
                best_match = candidate_skill

        item = {
            "requirement": requirement,
            "matched_with": best_match if best_score >= PARTIAL_THRESHOLD else None,
            "score": round(best_score, 2),
            "required": required,
        }

        if best_score >= MATCH_THRESHOLD:
            item["status"] = "matched"
            matched.append(item)

        elif best_score >= PARTIAL_THRESHOLD:
            item["status"] = "partial"
            partial.append(item)

        else:
            item["status"] = "missing"
            missing.append(item)

        scores.append(best_score)

    overall_score = (
        sum(scores) / len(scores)
        if scores
        else 100.0
    )

    required_missing = [
        item for item in missing + partial
        if item["required"]
    ]

    return {
        "score": round(overall_score, 2),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_missing": required_missing,
    }


# ============================================================
# EXPERIENCE DATE PARSING
# ============================================================

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def parse_date(text: str):
    if not text:
        return None

    text = text.lower().strip()

    # Month + year
    match = re.search(
        r"\b("
        + "|".join(MONTHS.keys())
        + r")\s+(\d{4})\b",
        text,
    )

    if match:
        month_name = match.group(1)
        year = int(match.group(2))

        return datetime(
            year,
            MONTHS[month_name],
            1,
        )

    # Year only
    match = re.search(r"\b(20\d{2})\b", text)

    if match:
        year = int(match.group(1))

        return datetime(
            year,
            1,
            1,
        )

    return None


def extract_years(duration: str) -> float:
    if not duration:
        return 0.0

    text = duration.lower().strip()

    # --------------------------------------------------------
    # Explicit years
    # --------------------------------------------------------

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:years?|yrs?)",
        text,
    )

    if match:
        return float(match.group(1))

    # --------------------------------------------------------
    # Explicit months
    # --------------------------------------------------------

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:months?|mos?)",
        text,
    )

    if match:
        return float(match.group(1)) / 12

    # --------------------------------------------------------
    # Month-Year range
    # Example:
    # Mar 2024 - Apr 2026
    # --------------------------------------------------------

    dates = re.findall(
        r"\b("
        + "|".join(MONTHS.keys())
        + r")\s+(\d{4})\b",
        text,
    )

    if len(dates) >= 2:

        start_month = MONTHS[dates[0][0]]
        start_year = int(dates[0][1])

        end_month = MONTHS[dates[1][0]]
        end_year = int(dates[1][1])

        months = (
            (end_year - start_year) * 12
            + (end_month - start_month)
            + 1
        )

        return max(months / 12, 0)

    # --------------------------------------------------------
    # Single month-year
    # Example:
    # July 2026
    # --------------------------------------------------------

    if len(dates) == 1:
        return 1 / 12

    # --------------------------------------------------------
    # Year range
    # Example:
    # 2022 - 2025
    # --------------------------------------------------------

    years = re.findall(r"\b(20\d{2})\b", text)

    if len(years) >= 2:

        start_year = int(years[0])
        end_year = int(years[1])

        return max(end_year - start_year + 1, 0)

    return 0.0


# ============================================================
# EXPERIENCE ROLE RELEVANCE
# ============================================================

def experience_role_score(
    requirement_role: str,
    experience,
) -> float:

    requirement = normalize(requirement_role)

    role = normalize(experience.role)

    description = normalize(
        experience.description
    )

    technologies = normalize(
        " ".join(experience.technologies)
    )

    candidate_text = " ".join(
        [
            role,
            description,
            technologies,
        ]
    )

    if not requirement or not candidate_text:
        return 0.0

    # --------------------------------------------------------
    # Direct role similarity
    # --------------------------------------------------------

    direct_role_score = similarity(
        requirement,
        role,
    )

    # --------------------------------------------------------
    # Backend-specific semantic evidence
    # --------------------------------------------------------

    if "backend" in requirement:

        backend_keywords = [
            "backend",
            "back end",
            "api",
            "rest api",
            "rest apis",
            "fastapi",
            "django",
            "flask",
            "node",
            "nodejs",
            "express",
            "mern",
            "server",
            "server side",
        ]

        matched_keywords = [
            keyword
            for keyword in backend_keywords
            if normalize(keyword) in candidate_text
        ]

        if matched_keywords:

            # Strong evidence from explicit backend terms
            if any(
                keyword in candidate_text
                for keyword in [
                    "backend",
                    "back end",
                    "fastapi",
                    "rest api",
                    "rest apis",
                ]
            ):
                return 95.0

            # Full-stack/MERN/API evidence
            if any(
                keyword in candidate_text
                for keyword in [
                    "mern",
                    "node",
                    "nodejs",
                    "express",
                    "api",
                ]
            ):
                return 85.0

    # --------------------------------------------------------
    # Generic concept matching
    # --------------------------------------------------------

    concept_score = concept_match_score(
        requirement_role,
        candidate_text,
    )

    return max(
        direct_role_score,
        concept_score,
    )


# ============================================================
# EXPERIENCE MATCHING
# ============================================================

def match_experience(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    matched = []
    partial = []
    missing = []

    all_scores = []

    for requirement in requirements.experience_requirements:

        best_role_score = 0.0
        best_experience = None

        # ----------------------------------------------------
        # Find the most relevant candidate experiences
        # ----------------------------------------------------

        for experience in resume.experience:

            score = experience_role_score(
                requirement.role,
                experience,
            )

            if score > best_role_score:
                best_role_score = score
                best_experience = experience

        # ----------------------------------------------------
        # Calculate TOTAL relevant experience
        # ----------------------------------------------------

        candidate_years = 0.0

        for experience in resume.experience:

            role_score = experience_role_score(
                requirement.role,
                experience,
            )

            # Only count reasonably relevant roles
            if role_score >= PARTIAL_THRESHOLD:

                candidate_years += extract_years(
                    experience.duration
                )

        candidate_years = round(
            candidate_years,
            2,
        )

        minimum_years = requirement.minimum_years

        # ----------------------------------------------------
        # Duration score
        # ----------------------------------------------------

        if minimum_years <= 0:

            duration_score = 100.0

        else:

            duration_ratio = (
                candidate_years / minimum_years
            )

            duration_score = min(
                duration_ratio * 100,
                100,
            )

        # ----------------------------------------------------
        # Combined experience score
        # ----------------------------------------------------

        if best_experience is None:

            final_score = 0.0

        else:

            final_score = (
                best_role_score * 0.35
                + duration_score * 0.65
            )

        final_score = round(
            final_score,
            2,
        )

        # ----------------------------------------------------
        # Build result
        # ----------------------------------------------------

        item = {
            "requirement": requirement.role,
            "minimum_years": minimum_years,
            "candidate_years": candidate_years,
            "role_match_score": round(
                best_role_score,
                2,
            ),
            "score": final_score,
            "required": requirement.required,
        }

        # ----------------------------------------------------
        # No relevant experience
        # ----------------------------------------------------

        if best_experience is None or best_role_score < PARTIAL_THRESHOLD:

            item["matched_with"] = None
            item["status"] = "missing"
            item["experience_status"] = "no_relevant_experience"

            missing.append(item)

        # ----------------------------------------------------
        # Relevant role + sufficient duration
        # ----------------------------------------------------

        elif (
            best_role_score >= MATCH_THRESHOLD
            and (
                minimum_years <= 0
                or candidate_years >= minimum_years
            )
        ):

            item["matched_with"] = best_experience.role
            item["status"] = "matched"
            item["experience_status"] = "requirement_satisfied"

            matched.append(item)

        # ----------------------------------------------------
        # Relevant role but insufficient duration
        # ----------------------------------------------------

        else:

            item["matched_with"] = best_experience.role
            item["status"] = "partial"
            item["experience_status"] = "insufficient_experience"

            partial.append(item)

        all_scores.append(final_score)

    overall_score = (
        sum(all_scores) / len(all_scores)
        if all_scores
        else 100.0
    )

    # --------------------------------------------------------
    # Mandatory experience gaps
    #
    # Important:
    # A requirement can be "partial" but still be a
    # mandatory gap if the candidate does not meet
    # the required number of years.
    # --------------------------------------------------------

    required_missing = []

    for item in matched + partial + missing:

        if not item["required"]:
            continue

        if (
            item["experience_status"]
            != "requirement_satisfied"
        ):
            required_missing.append(item)

    return {
        "score": round(
            overall_score,
            2,
        ),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_missing": required_missing,
    }






def is_ml_requirement(
    text: str,
) -> bool:

    text = normalize(text)

    ml_terms = [
        "machine learning",
        "machine-learning",
        " ml ",
        "scikit learn",
        "sklearn",
        "predictive modeling",
        "classification",
        "regression",
    ]

    return (
        "machine learning" in text
        or "machine-learning" in text
        or "scikit learn" in text
        or "sklearn" in text
        or "predictive modeling" in text
        or "classification" in text
        or "regression" in text
    )


def is_ml_project(
    text: str,
) -> bool:

    text = normalize(text)

    return any(
        term in text
        for term in [
            "machine learning",
            "machine-learning",
            "scikit learn",
            "sklearn",
            "predictive modeling",
            "classification",
            "regression",
            "tensorflow",
            "pytorch",
            "deep learning",
            "cnn",
            "neural network",
        ]
    )


def is_ai_requirement(
    text: str,
) -> bool:

    text = normalize(text)

    return (
        "artificial intelligence" in text
        or " ai " in f" {text} "
        or "computer vision" in text
        or "deep learning" in text
        or "neural network" in text
    )


def is_llm_requirement(text: str) -> bool:
    text = normalize(text)

    return any(
        term in text
        for term in [
            "llm",
            "large language model",
            "large language models",
            "generative ai",
            "genai",
            "language model",
            "rag",
            "retrieval augmented generation",
        ]
    )


def is_llm_project(text: str) -> bool:
    text = normalize(text)

    return any(
        term in text
        for term in [
            "llm",
            "large language model",
            "large language models",
            "generative ai",
            "genai",
            "language model",
            "rag",
            "retrieval augmented generation",
        ]
    )




def is_ai_project(
    text: str,
) -> bool:

    text = normalize(text)

    return (
        "artificial intelligence" in text
        or " ai " in f" {text} "
        or "computer vision" in text
        or "deep learning" in text
        or "neural network" in text
        or "cnn" in text
        or "opencv" in text
    )






def project_match_score(
    requirement: str,
    project: str,
) -> float:

    requirement = normalize(requirement)
    project = normalize(project)

    if not requirement or not project:
        return 0.0

    # AI OR LLM
    if (
        "ai or llm" in requirement
        or "llm or ai" in requirement
        or ("ai" in requirement and "llm" in requirement)
    ):
        if is_ai_project(project):
            return 100.0

        if is_llm_project(project):
            return 100.0

        if is_ml_project(project):
            return 75.0

        return similarity(requirement, project)

    # LLM only
    if is_llm_requirement(requirement):
        if is_llm_project(project):
            return 100.0

        return 0.0

    # AI only
    if is_ai_requirement(requirement):
        if is_ai_project(project):
            return 100.0

        if is_ml_project(project):
            return 80.0

        return 0.0

    # Machine Learning only
    if is_ml_requirement(requirement):
        if is_ml_project(project):
            return 100.0

        return 0.0

    # General project requirement
    return similarity(
        requirement,
        project,
    )





# ============================================================
# PROJECT MATCHING
# ============================================================

def match_projects(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    matched = []
    partial = []
    missing = []

    scores = []

    for requirement in requirements.project_requirements:

        requirement_text = normalize(
            requirement.requirement
        )

        best_score = 0.0
        best_project = None

        for project in resume.projects:

            project_text = normalize(
                " ".join(
                    [
                        project.name,
                        project.description,
                        " ".join(project.technologies),
                    ]
                )
            )

            score = project_match_score(
                requirement_text,
                project_text,
            )

            if score > best_score:

                best_score = score
                best_project = project

        item = {
            "requirement": requirement.requirement,
            "matched_with": (
                best_project.name
                if best_project
                and best_score >= PARTIAL_THRESHOLD
                else None
            ),
            "score": round(
                best_score,
                2,
            ),
            "required": requirement.required,
        }

        if best_score >= MATCH_THRESHOLD:

            item["status"] = "matched"
            matched.append(item)

        elif best_score >= PARTIAL_THRESHOLD:

            item["status"] = "partial"
            partial.append(item)

        else:

            item["status"] = "missing"
            missing.append(item)

        scores.append(best_score)

    overall_score = (
        sum(scores) / len(scores)
        if scores
        else 100.0
    )

    required_missing = [
        item
        for item in missing + partial
        if item["required"]
    ]

    return {
        "score": round(
            overall_score,
            2,
        ),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_missing": required_missing,
    }


# ============================================================
# EDUCATION MATCHING
# ============================================================

def education_match_score(
    requirement,
    education,
) -> float:

    required_degree = normalize(
        requirement.degree
    )

    required_field = normalize(
        requirement.field
    )

    candidate_degree = normalize(
        education.degree
    )

    candidate_field = normalize(
        education.field
    )

    # ========================================================
    # DEGREE MATCH
    # ========================================================

    degree_score = 0.0

    degree_terms = [
        "b.tech",
        "btech",
        "b.e",
        "be",
        "bachelor",
    ]

    required_degree_match = any(
        term in required_degree
        for term in degree_terms
    )

    candidate_degree_match = any(
        term in candidate_degree
        for term in degree_terms
    )

    if (
        required_degree_match
        and candidate_degree_match
    ):
        degree_score = 100.0

    else:
        degree_score = similarity(
            required_degree,
            candidate_degree,
        )


    # ========================================================
    # FIELD MATCH
    # ========================================================

    field_score = similarity(
        required_field,
        candidate_field,
    )


    # ========================================================
    # RELATED ENGINEERING FIELDS
    # ========================================================

    related_engineering_fields = [
        "electronics",
        "electrical",
        "instrumentation",
        "communication",
        "telecommunication",
        "computer",
        "information technology",
        "information systems",
        "software",
        "automation",
        "embedded",
        "robotics",
        "mechatronics",
    ]


    requires_computer_science = any(
        term in required_field
        for term in [
            "computer science",
            "related field",
        ]
    )


    candidate_is_related_engineering = any(
        term in (
            candidate_field
            + " "
            + candidate_degree
        )
        for term in related_engineering_fields
    )


    if (
        requires_computer_science
        and candidate_is_related_engineering
    ):

        field_score = max(
            field_score,
            88.0,
        )


    # ========================================================
    # FINAL EDUCATION SCORE
    # ========================================================

    return round(
        degree_score * 0.45
        + field_score * 0.55,
        2,
    )


def match_education(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    matched = []
    partial = []
    missing = []

    scores = []

    for requirement in requirements.education_requirements:

        best_score = 0.0
        best_education = None

        for education in resume.education:

            score = education_match_score(
                requirement,
                education,
            )

            if score > best_score:

                best_score = score
                best_education = education


        item = {
            "requirement": (
                f"{requirement.degree} "
                f"{requirement.field}"
            ),
            "matched_with": (
                f"{best_education.degree} - "
                f"{best_education.field}"
                if best_education
                and best_score >= PARTIAL_THRESHOLD
                else None
            ),
            "score": round(
                best_score,
                2,
            ),
            "required": requirement.required,
        }


        if best_score >= MATCH_THRESHOLD:

            item["status"] = "matched"
            matched.append(item)

        elif best_score >= PARTIAL_THRESHOLD:

            item["status"] = "partial"
            partial.append(item)

        else:

            item["status"] = "missing"
            missing.append(item)


        scores.append(best_score)


    overall_score = (
        sum(scores) / len(scores)
        if scores
        else 100.0
    )


    required_missing = [
        item
        for item in missing + partial
        if item["required"]
    ]


    return {
        "score": round(
            overall_score,
            2,
        ),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_missing": required_missing,
    }



# ============================================================
# CERTIFICATION MATCHING
# ============================================================

def match_certifications(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    matched = []
    partial = []
    missing = []

    scores = []

    candidate_certifications = resume.certifications

    for requirement in requirements.certifications:

        required_certification = requirement.certification

        best_score = 0.0
        best_match = None

        for candidate_certification in candidate_certifications:

            score = similarity(
                required_certification,
                candidate_certification,
            )

            if score > best_score:
                best_score = score
                best_match = candidate_certification

        item = {
            "requirement": required_certification,
            "matched_with": (
                best_match
                if best_score >= PARTIAL_THRESHOLD
                else None
            ),
            "score": round(best_score, 2),
            "required": requirement.required,
        }

        if best_score >= MATCH_THRESHOLD:

            item["status"] = "matched"
            matched.append(item)

        elif best_score >= PARTIAL_THRESHOLD:

            item["status"] = "partial"
            partial.append(item)

        else:

            item["status"] = "missing"
            missing.append(item)

        scores.append(best_score)

    overall_score = (
        sum(scores) / len(scores)
        if scores
        else 100.0
    )

    required_missing = [
        item
        for item in missing + partial
        if item["required"]
    ]

    return {
        "score": round(
            overall_score,
            2,
        ),
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "required_missing": required_missing,
    }






# ============================================================
# FINAL MATCHING
# ============================================================

def match_resume(
    resume: ResumeData,
    requirements: HRRequirements,
) -> dict:

    skills_result = match_skills(
        resume,
        requirements,
    )

    experience_result = match_experience(
        resume,
        requirements,
    )

    projects_result = match_projects(
        resume,
        requirements,
    )

    education_result = match_education(
        resume,
        requirements,
    )

    certifications_result = match_certifications(
        resume,
        requirements,
    )

    # --------------------------------------------------------
    # Weighted overall score
    # --------------------------------------------------------

    overall_score = (
        skills_result["score"] * WEIGHTS["skills"]
        + experience_result["score"] * WEIGHTS["experience"]
        + projects_result["score"] * WEIGHTS["projects"]
        + education_result["score"] * WEIGHTS["education"]
        + certifications_result["score"] * WEIGHTS["certifications"]
    )

    overall_score = round(
        overall_score,
        2,
    )

    # --------------------------------------------------------
    # Mandatory requirements
    # --------------------------------------------------------

    mandatory_gaps = []

    mandatory_gaps.extend(
        skills_result["required_missing"]
    )

    mandatory_gaps.extend(
        experience_result["required_missing"]
    )

    mandatory_gaps.extend(
        projects_result["required_missing"]
    )

    mandatory_gaps.extend(
        education_result["required_missing"]
    )

    mandatory_gaps.extend(
        certifications_result["required_missing"]
    )

    mandatory_total = (
        len(requirements.required_skills)

        + len(
            [
                x
                for x in requirements.experience_requirements
                if x.required
            ]
        )

        + len(
            [
                x
                for x in requirements.project_requirements
                if x.required
            ]
        )

        + len(
            [
                x
                for x in requirements.education_requirements
                if x.required
            ]
        )

        + len(
            [
                x
                for x in requirements.certifications
                if x.required
            ]
        )
    )

    # --------------------------------------------------------
    # Recommendation
    # --------------------------------------------------------

    if not mandatory_gaps:

        if overall_score >= MATCH_THRESHOLD:

            recommendation = "Strong Match"

        elif overall_score >= PARTIAL_THRESHOLD:

            recommendation = "Good Match"

        else:

            recommendation = "Weak Match"

    else:

        if overall_score >= MATCH_THRESHOLD:

            recommendation = "Strong Match - Mandatory Gaps"

        elif overall_score >= PARTIAL_THRESHOLD:

            recommendation = "Partial Match - Mandatory Gaps"

        else:

            recommendation = "Low Match - Mandatory Gaps"

    return {
        "overall_score": overall_score,
        "recommendation": recommendation,

        "mandatory_requirements": {
            "total": mandatory_total,
            "missing": len(mandatory_gaps),
            "all_satisfied": len(mandatory_gaps) == 0,
        },

        "skills": skills_result,
        "experience": experience_result,
        "projects": projects_result,
        "education": education_result,
        "certifications": certifications_result,
    }