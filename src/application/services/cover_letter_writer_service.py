from abc import ABC, abstractmethod
from typing import List, Optional
from attr import dataclass

@dataclass
class WriteCoverLetterResult:
    """Generic value object representing the result of a document retrieval operation."""
    success: bool
    message: str
    errors: Optional[List[str]] = None
    document: str = ""
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []    

class WriteCoverLetterCommand:
    def __init__(self, job_description: str, resume: str, applicant_name: str, company_website: str):
        self.job_description = job_description
        self.resume = resume
        self.applicant_name = applicant_name
        self.company_website = company_website

class CoverLetterWriterProvider(ABC):
    @abstractmethod
    async def write_cover_letter(self, command: WriteCoverLetterCommand) -> WriteCoverLetterResult:
        pass

class WriteCoverLetterService:
    def __init__(self, provider: CoverLetterWriterProvider):
        self._provider = provider

    async def execute(self, command: WriteCoverLetterCommand) -> WriteCoverLetterResult:
        result = await self._provider.write_cover_letter(command)
        return result
