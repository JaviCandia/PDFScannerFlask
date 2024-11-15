# PDF Chat Backend Application

This project is created as a learning exercise, utilizing **LangChain** and **Flask**. The application allows you to upload a PDF file and ask questions about its content, using the OpenAI API to provide responses.

## Installation

Follow these steps to set up and run the project in your local environment:

### Step 1: Clone the Repository

```bash
git clone https://github.com/your_username/your_repository_name.git
cd your_repository_name
```

### Step 2: Create and activate the Virtual Environment

Create the virtual environment

```bash
python -m venv venv
```

Activate the virtual environment

```bash
venv\Scripts\activate
```

### Step 3: Install Requirements

Install all the dependencies listed in requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 4: Run the application

Run the application using the following command:

```bash
python app.py
```

## Usage

### OpenAI API KEY
1. Rename the ``.env.example`` file to ``.env``.
2. Open the ``.env`` file and paste your OpenAI API Key into the file. It should look like this:
```bash
OPENAI_API_KEY=your_openai_api_key
```

### Upload your PDF

- Send a POST request to http://localhost:5000/upload with the PDF file.
- Use Postman or a similar tool, select "form-data" in the Body, and add a field named pdf with the file type set to "File".

### Ask Questions

- Send a POST request to http://localhost:5000/query with a JSON body containing the question.
- Example JSON

```json
{
  "question": "What is the main topic of the document?"
}
```
