from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    title: str = Field(description="Title of the research paper")
    authors: list[str] = Field(description="Paper authors")
    publication: str = Field(description="Conference, journal, or publication")


class AnalysisSection(BaseModel):
    content: str = Field(description="Detailed explanation")
    page_references: list[int] = Field(
        default_factory=list,
        description="Relevant PDF page numbers"
    )


class PaperAnalysis(BaseModel):
    metadata: PaperMetadata
    research_problem: AnalysisSection
    objectives: AnalysisSection
    methodology: AnalysisSection
    architecture: AnalysisSection
    experimental_setup: AnalysisSection
    datasets: AnalysisSection
    results: AnalysisSection
    contributions: AnalysisSection
    limitations: AnalysisSection
    executive_summary: str


class ReviewItem(BaseModel):
    claim: str
    assessment: str
    evidence: str
    page_references: list[int] = Field(default_factory=list)


class PaperReview(BaseModel):
    verification_results: list[ReviewItem]
    missing_information: list[str]
    unsupported_claims: list[str]
    methodology_assessment: str
    strengths: list[str]
    limitations: list[str]
    research_insights: list[str]
    future_research_questions: list[str]
    overall_assessment: str