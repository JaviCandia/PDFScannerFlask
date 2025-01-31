MATCH_TEMPLATE = """
                Based on the provided CV information: {documents}
                and the following roles: {roles},

                Perform the following tasks:

                1. Get the following personal information of the candidate:
                    - Name
                    - Phone number
                    - Email address
                    - State of residence
                    - City of residence
                    - Educational background

                2. Understand the Candidate's CV
                    - Determine the candidate's level based on their overall experience: Junior, Mid, or Senior.
                    - Identify and list the 7 primary skills/technologies.
                    - List all the companies where the candidate has worked.
                    - Get the candidate's English proficiency level.

                3. For each role, provide:
                    - Role name
                    - A short summary of the role description (maximum 3 lines)
                    - Identify A list of relevant skills from the candidate's CV that directly fit the role (maximum 3 skills).
                    - Analyze and make sure they are USEFUL skills/technologies that DIRECTLY match the role.
                    - A match score from 0 to 100 indicating how well the candidate fits the role. 0 if there are no skills that directly fit the role.
                    - Role start date.
                \n{format_instructions}
"""