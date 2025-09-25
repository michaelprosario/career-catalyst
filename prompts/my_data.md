Given
- I have the system open

When
- I can press a button called "my data"

Then
- The system navigates me to the "my data" configuration screen
- The "my data" configuration screen ables me to document the following information
    - my name
    - my resume(large text field)
    - my goals(large text field)
    - top accomplishments(large text fields)

====

Given
- I am using the "my data" screen
- I have filled out the entries on "my data"
When
- I click the save button

Then
- The system should ensure that the following fields are filled out: name, resume
- The system should store all data in separated mark down files in the "my_data" folder
- One file per field is fine
- This will enable an LLM to explore this data quickly





