from pydantic import BaseModel, Field
from typing import List, Optional

class EligibilityCriteriaRequest(BaseModel):
    age: Optional[int] = Field(None, ge=0, le=120, description="User age in years")
    state: Optional[str] = Field(None, description="State of residence (e.g. Tamil Nadu, Maharashtra)")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual household income in INR")
    category: Optional[str] = Field(None, description="Category (General, SC, ST, OBC, EWS)")
    disability_status: Optional[bool] = Field(None, description="Person with Disability (PwD)")
    pregnancy_status: Optional[bool] = Field(None, description="Pregnancy / Lactating status")
    gender: Optional[str] = Field(None, description="Gender (Female, Male, Other)")
    occupation: Optional[str] = Field(None, description="Occupation (e.g. Worker, Self-employed)")
    language: str = Field("en", description="Language code for output response")

class SchemeMatchItem(BaseModel):
    scheme_name: str = Field(..., description="Health scheme title")
    description: str = Field(..., description="Brief scheme summary")
    eligibility_notes: str = Field(..., description="Stated eligibility criteria from documents")
    required_documents: List[str] = Field(default_factory=list, description="List of required certificates/documents")
    source_document: str = Field(..., description="Source reference document")
    page: int = Field(..., description="Source page number")

class EligibilityGuidanceResponse(BaseModel):
    user_profile: dict = Field(..., description="Evaluated user profile criteria")
    matching_schemes: List[SchemeMatchItem] = Field(default_factory=list, description="Potentially relevant health schemes")
    guidance_notes: str = Field(..., description="Grounded explanation of scheme requirements")
    missing_information: List[str] = Field(default_factory=list, description="Fields required to narrow down eligibility")
    disclaimer: str = Field(..., description="Official eligibility disclaimer")

class SchemeSummary(BaseModel):
    scheme_name: str
    category: Optional[str] = None
    page: int
    file_source: str
