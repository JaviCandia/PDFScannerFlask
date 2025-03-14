MATCH_TEMPLATE = """
                Based on the provided CV information: {documents}

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

7. You are an AI assistant specialized in analyzing resumes. Your task is to extract the main technical skills from a PDF resume by identifying the most frequently mentioned skills in projects or job assignments. 
   Additionally, consider the number of years each skill has been used across different roles to determine the most relevant ones.

### Instructions:
7.1. **Extract skills**: Identify all technologies, programming languages, frameworks, and tools mentioned in the document.
7.2. **Calculate frequency**: Count how often each skill appears across different projects or job descriptions.
7.3. **Consider experience duration**: If the resume specifies years of experience per project, aggregate the total time for each skill.
7.4. **Prioritize main skills**: Select the top skills based on both frequency and years of experience.
7.5. **main_skills**: Return a concise list of the most relevant skills in the format:  '[Angular, React, Node.js, ...]'

### Example Output:
If the resume mentions Angular in 4 different projects spanning 6 years, React in 3 projects for 4 years, and Node.js in 5 projects for 7 years, the output should be:  
`["Node.js", "Angular", "React"]` (sorted based on relevance).

Process the PDF carefully and provide only the final list of skills.

                \n{format_instructions}
"""