


# TODO: LISTAR 10 SKILLS | OPTIMIZAR EL TEMPLATE

MATCH_TEMPLATE = """
                Based on the provided CV information: {documents}
                and the following roles: {roles},

                Please perform the following tasks:

                1. **Understand the Candidate CV**
                - Give me the name of the candidate.
                - Determine the candidate's level based on their overall experience: Junior, Mid or Senior.

                2. **List the Candidate's Main Skills and Experiences**:
                - Identify and enumerate the 5 primary skills / technologies.

                3. **List the companies where the candidate has worked for**
                - Identify all the companies where the candidate has worked.

                4. **Role Match**:
                - For each role, provide:
                    - The role name.
                    - A short summary of the role description, 3 lines maximum.
                    - Identify a list of relevant skills from candidate's CV that directly fit the role (5 maximum).
                    - If there are no relevant skills, indicate with a single bullet:
                        * There are no skills that fit the job position.
                    - A match score from 0 to 100 indicating how well the candidate fits the role. 0 If there are no skills that fit.
                    - Start date of the role.

                \n{format_instructions}
            """
