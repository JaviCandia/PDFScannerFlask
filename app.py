import os
from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
knowledge_base = None

# Initialize global embeddings model
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

@app.route('/upload', methods=['POST'])
def upload_pdf():
    global knowledge_base
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()

    # Filter out blank lines from the text
    text = "\n".join([line for line in text.split("\n") if line.strip() != ""])

    # Split text into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_text(text)

    # Use the pre-initialized embeddings model to create a knowledge base
    knowledge_base = FAISS.from_texts(chunks, embedding_model)

    return jsonify({'success': True, 'message': 'PDF processed successfully'})

@app.route('/query', methods=['POST'])
def query_pdf():
    global knowledge_base
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not initialized'}), 400

    user_question = request.json.get('question')
    os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
    docs = knowledge_base.similarity_search(user_question, 3)

    llm = Chat