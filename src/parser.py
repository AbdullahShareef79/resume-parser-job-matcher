import pdfplumber
import re
import spacy

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF resume."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_email(text):
    """Extract email from text using regex."""
    match = re.search(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    return match.group(0) if match else None

def extract_phone(text):
    """Extract phone number from text using regex."""
    match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,}", text)
    return match.group(0) if match else None

def extract_name(text):
    """Extract name using spaCy NER."""
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None

def extract_skills(text, skills_list):
    """Extract skills by matching with a predefined list."""
    found_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    return list(set(found_skills))

# Example skill set (can be expanded)
skills_list = ["Python", "Machine Learning", "Deep Learning", "NLP", "Data Science", "SQL"]

# Test the parser with a sample resume PDF
pdf_path = "sample_resume.pdf"  # Replace with an actual file path
resume_text = extract_text_from_pdf(pdf_path)

parsed_resume = {
    "Name": extract_name(resume_text),
    "Email": extract_email(resume_text),
    "Phone": extract_phone(resume_text),
    "Skills": extract_skills(resume_text, skills_list)
}

print(parsed_resume)
