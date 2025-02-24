import pdfplumber
import docx2txt
import spacy
import re
from collections import Counter
import os
import json
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("NLP model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load NLP model: {e}")
    raise

# Expanded skill database with categories
SKILLS_DB = {
    # Programming Languages
    "Python", "Java", "JavaScript", "C#", "C++", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "TypeScript",
    "R", "Scala", "Perl", "Shell", "Bash", "PowerShell", "MATLAB", "SQL", "NoSQL", "Haskell", "Julia",
    
    # Web Development
    "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "Spring", "ASP.NET",
    "jQuery", "Bootstrap", "Tailwind CSS", "WordPress", "Drupal", "Magento", "REST API", "GraphQL", "SOAP",
    
    # Data Science & ML
    "Machine Learning", "Deep Learning", "Natural Language Processing", "NLP", "Computer Vision", 
    "Data Science", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "SciPy",
    "NLTK", "spaCy", "XGBoost", "LightGBM", "PySpark", "Databricks", "Data Mining", "Feature Engineering",
    
    # Database
    "MySQL", "PostgreSQL", "MongoDB", "Oracle", "SQL Server", "Redis", "Elasticsearch", "Cassandra", "DynamoDB",
    "MariaDB", "Neo4j", "SQLite", "Firebase", "Supabase", "CosmosDB", "BigQuery",
    
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Google Cloud", "Terraform", "Jenkins", "CircleCI",
    "GitHub Actions", "GitLab CI", "Ansible", "Puppet", "Chef", "Prometheus", "Grafana", "ELK Stack",
    "Cloud Computing", "Serverless", "Lambda", "S3", "EC2", "CloudFormation", "Heroku", "Vercel", "Netlify",
    
    # Mobile Development
    "Android", "iOS", "React Native", "Flutter", "Xamarin", "Cordova", "Ionic", "Swift UI", "Jetpack Compose",
    "Mobile Development", "App Development",
    
    # Project Management & Methodologies
    "Agile", "Scrum", "Kanban", "Lean", "Waterfall", "JIRA", "Confluence", "Asana", "Trello", "Microsoft Project",
    "Product Management", "Project Management", "PMP", "PRINCE2", "Six Sigma",
    
    # Business & Data Analysis
    "Business Analysis", "Data Analysis", "Power BI", "Tableau", "Looker", "Data Visualization", "Statistical Analysis",
    "Excel", "Google Sheets", "A/B Testing", "SQL", "ETL", "Business Intelligence", "BI",
    
    # Soft Skills
    "Leadership", "Communication", "Teamwork", "Problem Solving", "Critical Thinking", "Time Management",
    "Organization", "Creativity", "Adaptability", "Flexibility", "Decision Making", "Prioritization",
    
    # Cybersecurity
    "Cybersecurity", "Network Security", "InfoSec", "Penetration Testing", "Vulnerability Assessment",
    "SIEM", "Firewall", "Encryption", "Security+", "CISSP", "CEH", "Ethical Hacking", "SOC", "Zero Trust"
}

# Phrasal skills need special handling
PHRASAL_SKILLS = {
    "Machine Learning", "Deep Learning", "Natural Language Processing", "Computer Vision", 
    "Data Science", "Cloud Computing", "Big Data", "Data Analysis", "Business Intelligence",
    "Project Management", "Mobile Development", "Web Development", "Full Stack", "Front End",
    "Back End", "DevOps", "Site Reliability Engineering", "UI/UX Design", "Artificial Intelligence",
    "Network Security", "Information Security", "Systems Administration", "Technical Support",
    "Customer Service", "Business Analysis", "Quality Assurance", "Test Automation"
}

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file with improved error handling.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if not text.strip():
            logger.warning(f"PDF file produced empty text: {pdf_path}")
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
    
    return text.strip()

def extract_text_from_docx(docx_path):
    """
    Extracts text from a DOCX file with improved error handling.
    
    Args:
        docx_path (str): Path to the DOCX file
        
    Returns:
        str: Extracted text
    """
    try:
        text = docx2txt.process(docx_path).strip()
        if not text:
            logger.warning(f"DOCX file produced empty text: {docx_path}")
        return text
    except Exception as e:
        logger.error(f"Error reading DOCX {docx_path}: {e}")
        return ""

def extract_name(text):
    """
    Extracts a person's name from the resume text using multiple methods.
    
    Args:
        text (str): Resume text
        
    Returns:
        str: Extracted name or None
    """
    # Method 1: NER for PERSON entities
    doc = nlp(text[:1000])  # Process just the first part for efficiency
    candidates = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    
    # Filter out common false positives
    common_false_positives = {"resume", "cv", "curriculum vitae", "experience", "education", 
                              "skills", "summary", "contact", "references"}
    candidates = [name for name in candidates if name.lower() not in common_false_positives]
    
    # Method 2: Check for common resume header patterns
    header_match = re.search(r"^([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,3})", text.split('\n')[0])
    if header_match:
        candidates.insert(0, header_match.group(1))  # Prioritize the header match
    
    # Return the most likely candidate if found
    if candidates:
        # Sort by length to favor full names over partial names
        candidates.sort(key=len, reverse=True)
        return candidates[0]
    
    return None

def extract_email(text):
    """
    Extracts an email address from the resume text.
    
    Args:
        text (str): Resume text
        
    Returns:
        str: Extracted email or None
    """
    # More comprehensive email regex
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_phone(text):
    """
    Extracts a phone number from the resume text with improved pattern matching.
    
    Args:
        text (str): Resume text
        
    Returns:
        str: Extracted phone number or None
    """
    # More comprehensive phone regex patterns
    patterns = [
        r"\(?\+?\d{1,3}?\)?[-.\s]?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{4}",
        r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\(\d{3}\)\s*\d{3}[-.\s]?\d{4}",
        r"\+\d{1,3}\s\d{2,4}\s\d{3,4}\s\d{4}"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None

def extract_education(text):
    """
    Extracts education information from the resume.
    
    Args:
        text (str): Resume text
        
    Returns:
        list: List of education entries
    """
    education = []
    
    # Look for education section
    edu_section = None
    
    # Common section headers for education
    education_headers = ["education", "academic background", "academic qualification", "qualifications"]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(header in line.lower() for header in education_headers):
            edu_section = i
            break
    
    if edu_section is not None:
        # Try to find degrees
        degree_patterns = [
            r"(bachelor|bs|b\.s\.|bachelor's|ba|b\.a\.|undergraduate)",
            r"(master|ms|m\.s\.|master's|ma|m\.a\.|graduate)",
            r"(ph\.?d\.?|doctor|doctorate)",
            r"(associate|a\.a\.|a\.s\.)",
            r"(mba|m\.b\.a\.)",
            r"(certificate|certification)"
        ]
        
        # Look for degree mentions and surrounding context
        for pattern in degree_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                # Get surrounding context (3 lines)
                pos = match.start()
                line_pos = text[:pos].count('\n')
                start_line = max(0, line_pos - 2)
                end_line = min(len(lines), line_pos + 3)
                
                degree_context = ' '.join(lines[start_line:end_line])
                education.append(degree_context.strip())
    
    # Deduplicate and clean
    unique_education = []
    for entry in education:
        if entry and not any(entry in existing for existing in unique_education):
            unique_education.append(entry)
    
    return unique_education

def extract_skills(text):
    """
    Extracts skills from the resume using improved NLP matching and pattern recognition.
    
    Args:
        text (str): Resume text
        
    Returns:
        list: List of extracted skills
    """
    # Normalize text
    normalized_text = " " + text.lower() + " "
    normalized_text = re.sub(r'[^\w\s]', ' ', normalized_text)
    normalized_text = re.sub(r'\s+', ' ', normalized_text)

    matched_skills = set()
    
    # First check for phrasal skills (multi-word skills)
    for skill in PHRASAL_SKILLS:
        if f" {skill.lower()} " in normalized_text:
            matched_skills.add(skill)
    
    # Check for single-word skills with word boundaries
    words = set(" " + word.lower() + " " for word in re.findall(r'\b\w+\b', normalized_text))
    for skill in SKILLS_DB:
        if " " not in skill and f" {skill.lower()} " in words:
            matched_skills.add(skill)
    
    # Use NLP-based similarity for broader skill detection
    doc = nlp(text)
    
    # Extract noun phrases which are often skills
    noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]
    
    # Check for any noun phrases that match our skills database
    for phrase in noun_phrases:
        normalized_phrase = phrase.lower()
        for skill in SKILLS_DB:
            if skill.lower() == normalized_phrase:
                matched_skills.add(skill)
    
    # Look for skill sections
    skill_section_pattern = r'(?:technical\s+)?(?:skills|proficiencies|competencies|expertise)[^\n]*(?:\n|:)(.*?)(?:\n\s*\n|\n[A-Z])'
    skill_match = re.search(skill_section_pattern, text, re.IGNORECASE | re.DOTALL)
    
    if skill_match:
        skill_text = skill_match.group(1)
        # Extract skills listed with commas or bullets
        skill_items = re.split(r'[,•\n]', skill_text)
        for item in skill_items:
            item = item.strip().lower()
            if item:
                for skill in SKILLS_DB:
                    if skill.lower() == item or skill.lower() in item.split():
                        matched_skills.add(skill)
    
    return sorted(list(matched_skills))

def extract_experience(text):
    """
    Extracts work experience information from the resume.
    
    Args:
        text (str): Resume text
        
    Returns:
        list: List of experience entries
    """
    experience = []
    
    # Try to locate experience section
    exp_section = None
    experience_headers = ["experience", "employment", "work history", "professional background", "professional experience"]
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(header in line.lower() for header in experience_headers):
            exp_section = i
            break
    
    if exp_section is not None:
        # Look for date patterns to identify different roles
        date_pattern = r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?|january|february|march|april|may|june|july|august|september|october|november|december)\.?\s+\d{4}\s*(?:–|-|to)\s*(?:((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?|january|february|march|april|may|june|july|august|september|october|november|december)\.?\s+\d{4}|present|current|now)"
        
        date_matches = list(re.finditer(date_pattern, text.lower()))
        
        # Process each job entry
        for i in range(len(date_matches)):
            start_pos = date_matches[i].start()
            
            # Find the end of this entry (next date or end of section)
            end_pos = text.lower().find('\n\n', start_pos)
            if i < len(date_matches) - 1:
                end_pos = min(end_pos if end_pos != -1 else len(text), date_matches[i+1].start())
            else:
                end_pos = end_pos if end_pos != -1 else len(text)
            
            # Extract the job entry
            job_entry = text[max(0, start_pos-100):end_pos].strip()
            if job_entry:
                experience.append(job_entry)
    
    return experience

def parse_resume(file_path):
    """
    Parses a resume file (PDF or DOCX) and extracts structured information.
    
    Args:
        file_path (str): Path to the resume file
        
    Returns:
        dict: Extracted information from the resume
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return {"error": "File not found"}
    
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension in [".docx", ".doc"]:
        text = extract_text_from_docx(file_path)
    else:
        logger.error(f"Unsupported file format: {file_extension}")
        return {"error": f"Unsupported file format: {file_extension}"}
    
    if not text:
        logger.error(f"Failed to extract text from file: {file_path}")
        return {"error": "Failed to extract text from file"}
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=4) as executor:
        name_future = executor.submit(extract_name, text)
        email_future = executor.submit(extract_email, text)
        phone_future = executor.submit(extract_phone, text)
        skills_future = executor.submit(extract_skills, text)
        education_future = executor.submit(extract_education, text)
        experience_future = executor.submit(extract_experience, text)
        
        name = name_future.result()
        email = email_future.result()
        phone = phone_future.result()
        skills = skills_future.result()
        education = education_future.result()
        experience = experience_future.result()
    
    result = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": education,
        "experience": experience,
    }
    
    logger.info(f"Successfully parsed resume: {file_path}")
    return result

def save_resume_data(resume_data, output_file):
    """
    Saves parsed resume data to a JSON file.
    
    Args:
        resume_data (dict): Parsed resume data
        output_file (str): Path to output file
    """
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2)
        logger.info(f"Resume data saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving resume data: {e}")
        return False