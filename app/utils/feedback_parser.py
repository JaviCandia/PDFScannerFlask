from typing import List, Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class RoleMatch(BaseModel):
    role: str = Field(description="Role Name")
    description: str = Field(description="Role description")
    relevant_skills: List[str] = Field(description="Relevant skills that fit the role. Empty array if there are no relevant skills" , default=[])
    start_date: str = Field(description="Role start date")
    score: int = Field(description="Match score")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "description": self.description,
            "relevant_skills": self.relevant_skills,
            "start_date": self.start_date,
            "score": self.score
        }

class FeedbackModel(BaseModel):
    name: str = Field(description="Name")
    phone: str = Field(description="Phone", default="")
    email: str = Field(description="Email", default="")
    state: str = Field(description="State", default="")
    city: str = Field(description="City", default="")
    english_level: str = Field(description="English level", default="")
    education: List[str] = Field(default_factory=list)
    years_experience: str = Field(description="Total work experience")
    companies: List[str] = Field(description="Companies")
    level: str = Field(description="Candidate level")
    skills: List[str] = Field(description="All skills")
    matches: List[RoleMatch] = Field(description="List of relevant roles matching the candidate skills", default=[])

    # [Experimental] General info:
    main_skills: List[str] = Field(description="Main skills", default=[])
    certs: List[str] = Field(description="Certificates list", default=[])
    previous_roles: List[str] = Field(description="Roles/Positions from previous jobs/projects", default=[])
    resume_type: str = Field(description="Internal or External", default="External")
    rehire: bool = Field(description="The candidate has been in accenture before?", default=False)

    # [Experimental] Accenture Resume:
    cl: int = Field(description="Career Level", default=0)
    current_project: str = Field(description="Current project", default="")
    roll_on_date: str = Field(description="Roll-On date", default="")
    roll_off_date: str = Field(description="Roll-Off date", default="")
  
    

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "state": self.state,
            "city": self.city,
            "english_level": self.english_level,
            "education": self.education,
             "years_experience": self.years_experience,
            "companies": self.companies,
            "level": self.level,
            "skills": self.skills,
            "matches": [role.to_dict() for role in self.matches],

            # [Experimental] General info:
            "main_skills": self.main_skills,
            "certs": self.certs,
            "previous_roles": self.previous_roles,
            "resume_type": self.resume_type,
            "rehire": self.rehire,

            # [Experimental] Accenture Resume:
            "cl": self.cl,
            "current_project": self.current_project,
            "roll_on_date": self.roll_on_date,
            "roll_off_date": self.roll_off_date
        }

feedback_parser = PydanticOutputParser(pydantic_object=FeedbackModel)
