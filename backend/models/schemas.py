from pydantic import BaseModel, Field


class Experience(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)


class Education(BaseModel):
    degree: str = ""
    field: str = ""
    institution: str = ""
    duration: str = ""


class ResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""

    skills: list[str] = Field(default_factory=list)

    experience: list[Experience] = Field(default_factory=list)

    projects: list[Project] = Field(default_factory=list)

    education: list[Education] = Field(default_factory=list)

    certifications: list[str] = Field(default_factory=list)