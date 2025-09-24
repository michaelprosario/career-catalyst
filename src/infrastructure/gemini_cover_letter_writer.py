"""
Gemini-based implementation of the cover letter writer provider.
Uses Google's Generative AI (Gemini Flash) to generate personalized cover letters.
"""
import os
import logging
from typing import Optional
import google.generativeai as genai

from src.application.services.cover_letter_writer_service import (
    CoverLetterWriterProvider,
    WriteCoverLetterCommand,
    WriteCoverLetterResult
)

logger = logging.getLogger(__name__)


class GeminiCoverLetterWriterProvider(CoverLetterWriterProvider):
    """
    Gemini-based implementation for generating cover letters.
    Uses Google's Generative AI API with Gemini Flash model.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the Gemini cover letter writer.
        
        Args:
            api_key: Google AI API key. If None, will use GOOGLE_AI_API_KEY environment variable
            model_name: Gemini model to use (default: gemini-1.5-flash)
        """
        self.model_name = model_name
        
        # Configure API key
        if api_key:
            genai.configure(api_key=api_key)
        else:
            api_key_env = os.getenv("GOOGLE_AI_API_KEY")
            if not api_key_env:
                raise ValueError(
                    "Google AI API key must be provided either as parameter or "
                    "GOOGLE_AI_API_KEY environment variable"
                )
            genai.configure(api_key=api_key_env)
        
        # Initialize the model
        self.model = genai.GenerativeModel(model_name)
        
    def _create_cover_letter_prompt(self, command: WriteCoverLetterCommand) -> str:
        """
        Create a detailed prompt for generating a cover letter.
        
        Args:
            command: The cover letter generation command with job details
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
You are an expert career consultant and professional writer specializing in creating compelling cover letters. 
Your task is to write a personalized, professional cover letter that effectively matches the candidate's 
qualifications to the job requirements.

## Plan cover letter
- Job description: Notice the key skills, qualifications, and responsibilities. Pay close attention to the keywords they use—these are the ones you should use in your letter.

A strong cover letter is a crucial part of a job application. It's your opportunity to go beyond your resume and tell a compelling story about why you are the best candidate for the specific job and company.

Here’s a breakdown of how to write a good cover letter:

### 1. Before You Write: Do Your Homework

* **Analyze the Job Description:** This is your primary source of information. Highlight the key skills, qualifications, and responsibilities. Pay close attention to the keywords they use—these are the ones you should use in your letter.
* **Research the Company:** Go beyond the job description. Look at their website, "About Us" page, recent press releases, and social media. What is their mission? What are their values? What projects have they recently completed? This research will help you tailor your letter and show genuine interest.
* **Find the Hiring Manager's Name:** A personalized greeting like "Dear [Hiring Manager's Name]" is always better than "Dear Hiring Manager" or "To Whom It May Concern." A quick search on LinkedIn or the company website can often help you find this information.

### 2. Structure Your Cover Letter

A good cover letter is typically one page long, consisting of three to four paragraphs.

* **Header:**
    * Your Name and Contact Information
    * Date

* **Paragraph 1: The Introduction**
    * State the position you are applying for and where you saw the job listing.
    * Start with a strong opening that grabs the reader's attention. Instead of "I am writing to apply for...", try an engaging statement that expresses your enthusiasm for the role and the company.
    * Briefly mention your most relevant qualification or achievement to hook the reader.

* **Paragraphs 2-3: The Body**
    * This is where you connect your skills and experience to the company's needs. **Do not simply repeat your resume.**
    * Use specific, quantifiable examples from resume. For instance, instead of saying "I am a strong leader," say, "In my previous role, I led a team that increased project efficiency by 15%, resulting in a 10% reduction in operating costs."
    * Focus on how your skills will solve the company's problems or help them achieve their goals, as outlined in the job description.
    * Demonstrate your research by mentioning something specific about the company, its mission, or a recent project that excites you. This shows you're not just sending a generic letter.

* **Paragraph 4: The Closing**
    * Reiterate your strong interest in the position and the company.
    * Express your confidence that you are a great fit for the role.
    * End with a clear call to action, such as expressing your eagerness to discuss your qualifications further in an interview.
    * Thank the reader for their time and consideration.

**Instructions:**
1. Write a formal, professional cover letter
2. Make specific connections between the candidate's experience and the job requirements
3. Show genuine interest in the company and role
4. Use a confident but not arrogant tone
5. Keep it concise (3-4 paragraphs, under 400 words)
6. Include proper business letter format
7. Avoid generic phrases and clichés
8. Make it ATS-friendly (no special formatting)

**Candidate Information:**
Name: {command.applicant_name}
Resume/Experience: 
{command.resume}

**Job Description:**
{command.job_description}

**Company Website/Information:** 
{command.company_website}

**Output Format:**
Generate only the cover letter content without any additional commentary or explanations. 
Start with the salutation and end with the closing.

**Cover Letter:**
"""
        return prompt.strip()
    
    async def write_cover_letter(self, command: WriteCoverLetterCommand) -> WriteCoverLetterResult:
        """
        Generate a cover letter using Gemini AI.
        
        Args:
            command: Cover letter generation parameters
            
        Returns:
            WriteCoverLetterResult with the generated cover letter or error details
        """
        try:
            # Validate inputs
            validation_errors = self._validate_command(command)
            if validation_errors:
                return WriteCoverLetterResult(
                    success=False,
                    message="Validation failed",
                    errors=validation_errors,
                    document=""
                )
            
            # Create the prompt
            prompt = self._create_cover_letter_prompt(command)
            
            # Generate the cover letter
            logger.info(f"Generating cover letter for {command.applicant_name}")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,  # Balanced creativity
                    max_output_tokens=1000,  # Reasonable length limit
                    top_p=0.9,
                    top_k=40
                )
            )
            
            if not response.text:
                return WriteCoverLetterResult(
                    success=False,
                    message="No content generated by AI model",
                    errors=["Empty response from Gemini API"],
                    document=""
                )
            
            cover_letter = response.text.strip()
            
            logger.info("Cover letter generated successfully")
            return WriteCoverLetterResult(
                success=True,
                message="Cover letter generated successfully",
                errors=[],
                document=cover_letter
            )
            
        except Exception as e:
            error_msg = f"Failed to generate cover letter: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return WriteCoverLetterResult(
                success=False,
                message=error_msg,
                errors=[str(e)],
                document=""
            )
    
    def _validate_command(self, command: WriteCoverLetterCommand) -> list[str]:
        """
        Validate the cover letter generation command.
        
        Args:
            command: The command to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        if not command.applicant_name or not command.applicant_name.strip():
            errors.append("Applicant name is required")
        
        if not command.job_description or not command.job_description.strip():
            errors.append("Job description is required")
        
        if not command.resume or not command.resume.strip():
            errors.append("Resume/experience information is required")
        
        # Company website is optional, so we don't validate it as required
        
        return errors
