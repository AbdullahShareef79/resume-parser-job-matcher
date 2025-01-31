# Resume Parser & Job Matcher

An intelligent system that parses resumes, extracts key information, and matches candidates with relevant job opportunities using semantic similarity.

## Features

- 📄 Resume parsing for PDF and DOCX formats
- 🔧 Skills extraction using spaCy and custom patterns
- 🧠 Semantic job matching with Sentence Transformers
- 🚀 FastAPI backend with Swagger documentation
- 📊 ESCO skills database integration
- 🔍 Cosine similarity-based ranking system

## Installation

### Prerequisites
- Python 3.10+
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/AbdullahShareef79/resume-parser-job-matcher.git
cd resume-parser-job-matcher

## **Install dependencies
**
pip install -r requirements.txt
python -m spacy download en_core_web_trf
python -m nltk.downloader punkt wordnet stopwords
