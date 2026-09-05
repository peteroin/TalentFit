from .services.document_parser import extract_resume_text
from .services.resume_extractor import extract_resume_data


file_path = "uploads/resume.pdf"


resume_text = extract_resume_text(file_path)

print("\n")
print("=" * 80)
print("RAW RESUME TEXT")
print("=" * 80)

print(resume_text)


resume_data = extract_resume_data(resume_text)

print("\n")
print("=" * 80)
print("STRUCTURED RESUME")
print("=" * 80)

print(resume_data.model_dump_json(indent=4))