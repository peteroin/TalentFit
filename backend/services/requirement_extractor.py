import os

from dotenv import load_dotenv
from groq import Groq

from ..models.hr_schemas import HRRequirements


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
# HR REQUIREMENT JSON SCHEMA
# ============================================================

HR_REQUIREMENT_SCHEMA = {
    "type": "object",

    "properties": {

        "required_skills": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "preferred_skills": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },

        "experience_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string"
                    },
                    "minimum_years": {
                        "type": "number"
                    },
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "role",
                    "minimum_years",
                    "required"
                ],
                "additionalProperties": False
            }
        },

        "project_requirements": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "requirement": {
                        "type": "string"
                    },
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "requirement",
                    "required"
                ],
                "additionalProperties": False
            }
        },

        "education_requirements": {
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
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "degree",
                    "field",
                    "required"
                ],
                "additionalProperties": False
            }
        },

        "certifications": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "certification": {
                        "type": "string"
                    },
                    "required": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "certification",
                    "required"
                ],
                "additionalProperties": False
            }
        }
    },

    "required": [
        "required_skills",
        "preferred_skills",
        "experience_requirements",
        "project_requirements",
        "education_requirements",
        "certifications"
    ],

    "additionalProperties": False
}


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an expert HR job-requirement extraction system.

Extract hiring requirements from the provided job description
or HR requirement text.

Return ONLY the JSON object required by the supplied schema.

Rules:

1. Extract mandatory requirements separately from preferred
   requirements.

2. A requirement described as:
   - required
   - mandatory
   - must-have
   - minimum
   - essential
   should be marked required=true.

3. A requirement described as:
   - preferred
   - nice-to-have
   - bonus
   - optional
   - desirable
   should be marked required=false.

4. Extract technical skills.

5. Required technical skills go into required_skills.

6. Preferred technical skills go into preferred_skills.

7. Extract minimum years of experience when explicitly mentioned.

8. Extract relevant job roles.

9. Extract project requirements.

10. Extract education requirements.

11. Extract certifications.

12. Every certification must contain:
    - certification
    - required

13. Do not invent requirements.

14. If a value is not mentioned, use an empty string,
    zero, or an empty list as appropriate.

15. Do not provide explanations outside the JSON object.
"""


# ============================================================
# HR REQUIREMENT EXTRACTION
# ============================================================

def extract_hr_requirements(
    requirement_text: str
) -> HRRequirements:

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
                    "Extract the structured hiring requirements "
                    "from the following text:\n\n"
                    + requirement_text
                )
            }
        ],

        reasoning_effort="low",
        include_reasoning=False,

        temperature=0,

        max_completion_tokens=4096,

        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "hr_requirements",
                "strict": True,
                "schema": HR_REQUIREMENT_SCHEMA
            }
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError(
            "Groq returned an empty response."
        )

    return HRRequirements.model_validate_json(content)