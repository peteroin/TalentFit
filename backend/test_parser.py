from .services.document_parser import extract_resume_text


file_path = "uploads/resume.pdf"

text = extract_resume_text(file_path)

print("=" * 80)
print("EXTRACTED RESUME TEXT")
print("=" * 80)

print(text)

print("=" * 80)
print(f"Characters extracted: {len(text)}")
print(f"Words extracted: {len(text.split())}")