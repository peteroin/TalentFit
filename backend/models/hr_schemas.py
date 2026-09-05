from pydantic import BaseModel, Field


class ExperienceRequirement(BaseModel):
    role: str = ""
    minimum_years: float = 0
    required: bool = True


class ProjectRequirement(BaseModel):
    requirement: str = ""
    required: bool = True


class EducationRequirement(BaseModel):
    degree: str = ""
    field: str = ""
    required: bool = True


class CertificationRequirement(BaseModel):
    certification: str = ""
    required: bool = True


class HRRequirements(BaseModel):
    required_skills: list[str] = Field(default_factory=list)

    preferred_skills: list[str] = Field(default_factory=list)

    experience_requirements: list[
        ExperienceRequirement
    ] = Field(default_factory=list)

    project_requirements: list[
        ProjectRequirement
    ] = Field(default_factory=list)

    education_requirements: list[
        EducationRequirement
    ] = Field(default_factory=list)

    certifications: list[
        CertificationRequirement
    ] = Field(default_factory=list)