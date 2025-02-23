import pdfplumber
import docx2txt
import spacy
import re
from collections import Counter

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Skill database (expandable)
SKILLS_DB = {
    "Python", "Java", "C++", "SQL", "Machine Learning", "Deep Learning",
    "NLP", "Computer Vision", "Data Science", "TensorFlow", "PyTorch",
    "Keras", "Docker", "Kubernetes", "Cloud Computing", "React", "Node.js"
}

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    try:
        return docx2txt.process(docx_path).strip()
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def extract_name(text):
    """Extracts a person's name from the resume text."""
    doc = nlp(text)
    candidates = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Filter out common false positives
    common_false_positives = {"experience", "education", "skills", "summary"}
    candidates = [name for name in candidates if name.lower() not in common_false_positives]
    
    return candidates[0] if candidates else None

def extract_email(text):
    """Extracts an email address from the resume text."""
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    """Extracts a phone number from the resume text."""
    match = re.search(r"\(?\+?\d{1,3}?\)?[-.\s]?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}", text)
    return match.group() if match else None

def extract_skills(text):
    """Extracts skills from the resume using NLP matching."""
    words = set(word.lower() for word in text.split())

    # Check for exact matches in the skills database
    matched_skills = {skill for skill in SKILLS_DB if skill.lower() in words}

    # Use NLP-based similarity for broader skill detection
    doc = nlp(text)
    for token in doc:
        if token.text.lower() in SKILLS_DB:
            matched_skills.add(token.text)

    return list(matched_skills)

def parse_resume(file_path):
    """Parses a resume file (PDF or DOCX) and extracts structured information."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        return {"error": "Unsupported file format"}

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
    }
