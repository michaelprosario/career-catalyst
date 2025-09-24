"""
Test the Gemini cover letter writer implementation
"""
import asyncio
import os
from src.infrastructure.gemini_cover_letter_writer import GeminiCoverLetterWriterProvider
from src.application.services.cover_letter_writer_service import WriteCoverLetterCommand

## include dotenv
from dotenv import load_dotenv
load_dotenv()

async def test_cover_letter_writer():
    """Test the Gemini cover letter writer with sample data."""
    
    # Create sample data
    command = WriteCoverLetterCommand(
        job_description="""
        Software Engineer Position at TechCorp
        
        We are seeking a passionate Software Engineer to join our growing team. 
        The ideal candidate will have experience with:
        - Python programming
        - Web development frameworks
        - Database design
        - API development
        - Agile methodologies
        
        Requirements:
        - 3+ years of software development experience
        - Strong problem-solving skills
        - Experience with cloud platforms
        - Excellent communication skills
        """,
        resume="""
        John Smith - Software Developer
        
        Experience:
        - 4 years as Python developer at StartupXYZ
        - Built REST APIs using FastAPI and Flask
        - Worked with PostgreSQL and MongoDB databases
        - Deployed applications on AWS
        - Collaborated in Agile/Scrum teams
        - Led junior developers on multiple projects
        
        Skills: Python, JavaScript, SQL, Docker, AWS, Git
        """,
        applicant_name="John Smith",
        company_website="https://techcorp.com - Leading technology solutions provider"
    )
    
    try:
        # Initialize the provider (will use GOOGLE_AI_API_KEY env var if available)
        provider = GeminiCoverLetterWriterProvider()
        
        # Generate cover letter
        print("Generating cover letter...")
        result = await provider.write_cover_letter(command)
        
        if result.success:
            print("✅ Cover letter generated successfully!")
            print("\n" + "="*60)
            print("GENERATED COVER LETTER:")
            print("="*60)
            print(result.document)
            print("="*60)
        else:
            print("❌ Failed to generate cover letter:")
            print(f"Message: {result.message}")
            print(f"Errors: {result.errors}")
            
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nTo test this, set the GOOGLE_AI_API_KEY environment variable:")
        print("export GOOGLE_AI_API_KEY='your-api-key-here'")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(test_cover_letter_writer())