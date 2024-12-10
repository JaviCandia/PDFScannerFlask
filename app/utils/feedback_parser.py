from typing import List, Dict, Any
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class RoleMatch(BaseModel):
    role_name: str = Field(description="Name of the role")
    role_description: str = Field(description="Short summary of the role descirption")
    fit_skills: List[str] = Field(description="Skills from the candidate that fit the role. Empty array if there are no roles")
    start_date: str = Field(description="Role start date")
    match_score: int = Field(description="Score from 0 to 100 indicating how the candidate fits the role")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role_name": self.role_name, 
            "role_description": self.role_description,
            "fit_skills": self.fit_skills, 
            "start_date": self.start_date,
            "match_score": self.match_score
        }

class FeedbackModel(BaseModel):
    candidate_name: str = Field(description="Name of the candidate")
    # experience_years: int = Field(description="Years of experience of the candidate")
    companies: List[str] = Field(description="Companies where the candidate has worked")
    candidate_level: str = Field(description="Candidate level")
    main_skills: List[str] = Field(description="Main skills from the candidate CV")
    role_matches: List[RoleMatch] = Field(description="List of role matches with the candidate")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_name": self.candidate_name,
            # "experience_years": self.experience_years,
            "companies": self.companies,
            "candidate_level": self.candidate_level,
            "main_skills": self.main_skills, 
            "role_matches": [role_match.to_dict() for role_match in self.role_matches]
        }

feedback_parser = PydanticOutputParser(pydantic_object=FeedbackModel)
