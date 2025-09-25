Given
- I am using the "view opportunity detail" screen
- I see the "draft cover letter" button

When
- I click the "draft cover letter" button

Then 
- the system uses the src/infrastructure/gemini_cover_letter_writer.py to draft a cover letter
- the system should populate job description details from the opportunity record
- the system should populate resume and name details from "my_data"