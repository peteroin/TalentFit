from .services.requirement_extractor import extract_hr_requirements


requirement_text = """
We are looking for a Backend Developer.

Required skills:
Python
FastAPI
SQL
Docker
Git

Preferred skills:
AWS
Kubernetes

Experience:
At least 2 years of backend development experience.

The candidate should have experience building REST APIs.

Projects:
At least one Machine Learning project.
Experience with an AI or LLM project is preferred.

Education:
B.Tech or B.E. in Computer Science or related field.

Certification:
AWS certification is preferred.
"""


requirements = extract_hr_requirements(requirement_text)


print("=" * 80)
print("HR REQUIREMENTS")
print("=" * 80)

print(requirements.model_dump_json(indent=4))