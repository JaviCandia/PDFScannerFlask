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
    # years_experience: int = Field(description="Years of experience")
    companies: List[str] = Field(description="Companies")
    level: str = Field(description="Candidate level")
    skills: List[str] = Field(description="Primary Skills")
    roles: List[RoleMatch] = Field(description="List of relevant roles matching the candidate skills", default=[])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "state": self.state,
            "city": self.city,
            "english_level": self.english_level,
            "education": self.education,
            # "years_experience": self.years_experience,
            "companies": self.companies,
            "level": self.level,
            "skills": self.skills,
            "roles": [role.to_dict() for role in self.roles],
        }

feedback_parser = PydanticOutputParser(pydantic_object=FeedbackModel)
