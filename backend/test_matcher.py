from .models.schemas import (
    ResumeData,
    Experience,
    Project,
    Education,
)

from .models.hr_schemas import (
    HRRequirements,
    ExperienceRequirement,
    ProjectRequirement,
    EducationRequirement,
    CertificationRequirement,
)

from .services.matcher import match_resume


# ============================================================
# MOCK RESUME
# ============================================================

resume = ResumeData(
    name="Peter Kumar",

    email="peter.userid@gmail.com",

    phone="+91-9060268964",

    skills=[
        "Python",
        "C/C++",
        "SQL",
        "OOPs",
        "DBMS",
        "Machine Learning",
        "Deep Learning",
        "Large Language Models",
        "TensorFlow",
        "FastAPI",
        "Git/Github",
        "Hugging Face",
        "ML-Flow",
        "Docker",
        "CI/CD",
        "Linux",
        "NumPy",
        "Pandas",
        "Matplotlib",
        "Seaborn",
        "HTML",
        "CSS",
        "JavaScript",
        "React",
        "MERN",
    ],

    experience=[
        Experience(
            company="Web Stack Academy (WSA)",
            role="Full Stack Web Development Intern",
            duration="Mar 2026 – Apr 2026",
            description=(
                "Gained hands-on exposure to HTML, CSS, JavaScript, "
                "and React for frontend development. Worked with "
                "SDLC-based project development using the MERN stack."
            ),
            technologies=[
                "HTML",
                "CSS",
                "JavaScript",
                "React",
                "MERN",
            ],
        ),

        Experience(
            company=(
                "Damodar Valley Corporation (DVC), "
                "Durgapur Steel Thermal Power Station"
            ),
            role="Vocational Trainee",
            duration="Jul 2026",
            description=(
                "Gained knowledge of measurement and control systems "
                "used in thermal power plant operations."
            ),
            technologies=[
                "Instrumentation",
                "Measurement Systems",
            ],
        ),
    ],

    projects=[
        Project(
            name=(
                "Disaster Casualties Prediction using ML Tools "
                "for Enhanced Resource Planning"
            ),
            description=(
                "Developed a machine learning system to predict "
                "fatalities, affected population, homeless population, "
                "and disaster duration using historical disaster datasets."
            ),
            technologies=[
                "Python",
                "Scikit-learn",
                "Pandas",
                "NumPy",
                "Feature Engineering",
            ],
        ),

        Project(
            name="AI Interview Behavior Analyzer",
            description=(
                "Developed a CNN-based realtime video analysis system "
                "to detect facial expressions, attention levels, and "
                "engagement patterns during mock interviews."
            ),
            technologies=[
                "Python",
                "OpenCV",
                "CNN",
            ],
        ),
    ],

    education=[
        Education(
            degree="B.Tech",
            field="Applied Electronics & Instrumentation Engineering",
            institution="Heritage Institute of Technology",
            duration="2027",
        ),
    ],

    certifications=[],
)


# ============================================================
# MOCK HR REQUIREMENTS
# ============================================================

requirements = HRRequirements(

    required_skills=[
        "Python",
        "FastAPI",
        "SQL",
        "Docker",
        "Git",
    ],

    preferred_skills=[
        "AWS",
        "Kubernetes",
    ],

    experience_requirements=[
        ExperienceRequirement(
            role="backend development",
            minimum_years=2,
            required=True,
        ),
    ],

    project_requirements=[
        ProjectRequirement(
            requirement="At least one Machine Learning project.",
            required=True,
        ),

        ProjectRequirement(
            requirement="Experience with an AI or LLM project.",
            required=False,
        ),
    ],

    education_requirements=[
        EducationRequirement(
            degree="B.Tech or B.E.",
            field="Computer Science or related field",
            required=True,
        ),
    ],

    certifications=[
        CertificationRequirement(
            certification="AWS certification",
            required=False,
        ),
    ],
)


# ============================================================
# RUN MATCHING
# ============================================================

result = match_resume(
    resume,
    requirements,
)


# ============================================================
# DISPLAY RESULT
# ============================================================

import json

print()
print("=" * 80)
print("RESUME MATCHING RESULT")
print("=" * 80)

print(
    json.dumps(
        result,
        indent=4,
    )
)