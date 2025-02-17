MATCH_TEMPLATE = """
                Based on the provided CV information: {documents}
                and the following roles: {roles},

                Perform the following tasks:

                1. Get the following personal information of the candidate:
                    - Name.
                    - Phone number.
                    - Email address.
                    - State of residence.
                    - City of residence.
                    - Educational background.

                2. Understand the Candidate's CV:
                    - Determine the candidate's level based on their overall experience: Junior, Mid, or Senior.
                    - Identify and list all the skills/technologies of the candidate.
                    - Identify and list the 3 main skills/technologies of the candidate based on how often they are mentioned or years of experience detected.
                    - List all the companies where the candidate has worked.
                    - Rehire: determine if the employee has been in accenture before (True/False).
                    - Get the candidate's English proficiency level.
                    - Get the list of certifications the candidate has (usually there is a section for this).
                    - Get the roles/positions the candidate has had in previous jobs/projects.
                
                3. Determine if the resume it's internal or external:
                    - Resume type: internal if email address is from @accenture.com, external if not.
                
                4. Extract this information if the resume is internal:
                    - career level (cl): Accenture Career Level (1 - 12).
                    - Current project.
                    - Roll-On date.
                    - Roll-Off date.

                4. For each role, provide:
                    - Role name.
                    - roleId.
                    - A short summary of the role description (maximum 3 lines).
                    - Identify A list of relevant skills from the candidate's CV that directly fit the role (maximum 3 skills).
                    - Analyze and make sure they are USEFUL skills/technologies that DIRECTLY match the role.
                    - A match score from 0 to 100 indicating how well the candidate fits the role. 0 if there are no skills that directly fit the role.
                    - Role start date.

               5.You are an AI specialized in analyzing resumes. Your task is to extract and calculate the total years of work experience based on the candidate's job history.

               ### **Instructions:**
               5.1. Identify **job entries** that contain:
                  - A **role title** (e.g., "Software Engineer").
                  - A **company name** (e.g., "Globant", "Accenture").
                  - **Start and end dates**, which are usually found **immediately after** the role title or company name.

               5.2. **Extract employment dates:**
                  - Locate the **earliest job start date** (first recorded job).
                  - Locate the **most recent job end date** (last recorded job).
                  - If the last job is ongoing (e.g., "Present" or "Current"), assume today's date as the end date.

               5.3. **Supported Date Formats:**
                  - **Month-Year:** (e.g., "April 2021 – February 2024").
                  - **Year only:** (e.g., "2018 – 2019").
                  - **Text-based:** (e.g., "March 2019 – Present").
                  - **Abbreviations:** (e.g., "Jan. 2018 – June 2018").

               5.4. **Calculate total work experience:**
                  - Compute the difference between the **first job start date** and the **last job end date**.
                  - Convert the difference into **years and months**.
                  - Exclude gaps between jobs unless explicitly stated.

               5.5. **Ensure correctness by checking all jobs listed:**
                  - The **first employment start date** should be the earliest recorded work experience (e.g., **January 2018**).
                  - The **most recent job should be considered ongoing if no end date is provided**, meaning today's date should be used for the calculation.

               5.6. **Ignore irrelevant data:**
                  - Do not consider internships, academic projects, or unpaid roles unless explicitly stated as "full-time experience."
                  - Exclude overlapping jobs from duplicate calculations.

               ### **Expected Output Format:**
               - **First employment start date:** YYYY-MM  
               - **Last employment end date:** YYYY-MM (or "Present" if ongoing)  
               - **Total work experience:** X years, Y months  

               ### **Example Input (Resume Excerpt):**

               6. Extract key information from the provided CV and summarize the candidate's experience in the following format:
               - Summary: '[Job Role] with [X] years of experience in [Key Technologies/Skills]'.
               - Ensure that the extracted information is concise, accurate, and reflects the candidate’s primary expertise.

                \n{format_instructions}
"""