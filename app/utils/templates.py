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
                    - A short summary of the role description (maximum 3 lines).
                    - Identify A list of relevant skills from the candidate's CV that directly fit the role (maximum 3 skills).
                    - Analyze and make sure they are USEFUL skills/technologies that DIRECTLY match the role.
                    - A match score from 0 to 100 indicating how well the candidate fits the role. 0 if there are no skills that directly fit the role.
                    - Role start date.
                \n{format_instructions}
"""