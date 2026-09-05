import os

from dotenv import load_dotenv
from groq import Groq

from ..models.schemas import ResumeData


# ============================================================
# GROQ CONFIGURATION
# ============================================================

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is not configured in the .env file."
    )

client = Groq(api_key=api_key)


# ============================================================
# RESUME JSON SCHEMA
# ============================================================

RESUME_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "email": {
            "type": "string"
        },
        "phone": {
            "type": "string"
        },
        "skills": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "experience": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "company": {
                        "type": "string"
                    },
                    "role": {
                        "type": "string"
                    },
                    "duration": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "technologies": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "company",
                    "role",
                    "duration",
                    "description",
                    "technologies"
                ],
                "additionalProperties": False
            }
        },
        "projects": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "technologies": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "name",
                    "description",
                    "technologies"
                ],
                "additionalProperties": False
            }
        },
        "education": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "degree": {
                        "type": "string"
                    },
                    "field": {
                        "type": "string"
                    },
                    "institution": {
                        "type": "string"
                    },
                    "duration": {
                        "type": "string"
                    }
                },
                "required": [
                    "degree",
                    "field",
                    "institution",
                    "duration"
                ],
                "additionalProperties": False
            }
        },
        "certifications": {
            "type": "array",
            "items": {
                "type": "string"
            }
        }
    },
    "required": [
        "name",
        "email",
        "phone",
        "skills",
        "experience",
        "projects",
        "education",
        "certifications"
    ],
    "additionalProperties": False
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a resume information extraction system.

Extract structured information ONLY from the resume text.

Return ONLY the JSON object required by the schema.

Rules:

1. Never invent information.
2. Extract only information explicitly present in the resume.
3. Extract all relevant technical skills.
4. Extract professional work experience.
5. Extract projects.
6. Extract education.
7. Extract certifications.
8. Extract technologies mentioned in each experience and project.
9. Keep descriptions short and factual.
10. Do not include achievements as projects.
11. Do not include positions of responsibility as work experience.
12. If a field is unavailable, return an empty string.
13. If a list is unavailable, return an empty list.
14. Do not provide explanations outside the JSON object.
"""


# ============================================================
# RESUME EXTRACTION
# ============================================================

def extract_resume_data(resume_text: str) -> ResumeData:

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": (
                    "Extract the structured resume information "
                    "from the following resume:\n\n"
                    + resume_text
                )
            }
        ],

        # GPT-OSS reasoning can consume completion tokens.
        # Low reasoning is enough for structured extraction.
        reasoning_effort="low",

        # Do not return reasoning in the response.
        include_reasoning=False,

        temperature=0,

        # Give the model enough room to finish valid JSON.
        max_completion_tokens=8192,

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "resume_data",
                "strict": True,
                "schema": RESUME_SCHEMA
            }
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )

    return ResumeData.model_validate_json(content)