Here’s the **single-block README.md** for easy copy-pasting:

```markdown
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
```

2. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
python -m nltk.downloader punkt wordnet stopwords
```

3. Download ESCO skills dataset and place in `data/` directory:
```bash
wget -P data/ https://esco.ec.europa.eu/sites/default/files/esco_skills.csv
```

## Usage

### Run the API server:
```bash
python -m backend.main
```

The API will be available at:
- Documentation: http://localhost:8000/docs
- Endpoint: http://localhost:8000/upload

### Example API Request:
```bash
curl -X 'POST' \
  'http://localhost:8000/upload/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@path/to/your/resume.pdf;type=application/pdf'
```

## Project Structure
```
resume-parser-job-matcher/
├── backend/
│   ├── main.py              # FastAPI server and routes
│   ├── job_matcher.py       # Job matching logic
│   ├── resume_parser.py     # Resume parsing implementation
│   └── __init__.py
├── data/
│   └── esco_skills.csv      # ESCO skills database
├── models/                  # Saved ML models
├── notebooks/               # Jupyter notebooks for experimentation
├── frontend/                # (Future) Web interface
├── requirements.txt         # Dependency list
└── README.md                # This document
```

## API Documentation

### POST /upload/
Upload a resume file (PDF/DOCX) and get parsed data with job matches

**Parameters:**
- `file`: Resume file to upload

**Response:**
```json
{
  "filename": "resume.pdf",
  "parsed_data": {
    "skills": "python machine-learning data-analysis",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "matched_jobs": [
    {
      "title": "Software Engineer",
      "company": "Tech Corp",
      "similarity_score": 0.95,
      ...
    }
  ]
}
```

## Technologies Used
- **Natural Language Processing**: spaCy, NLTK
- **Semantic Matching**: Sentence Transformers
- **Backend**: FastAPI, Uvicorn
- **File Parsing**: pdfplumber, docx2txt
- **Machine Learning**: scikit-learn, transformers

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
Abdullah Shareef  
abdullah@example.com  
[Project Link](https://github.com/AbdullahShareef79/resume-parser-job-matcher)
```

---

### How to Use:
1. Copy the entire block above.
2. Create a new file named `README.md` in the root of your project.
3. Paste the content into the file.
4. Save the file and commit it to your repository.

This version is formatted as a single block for easy copy-pasting. Let me know if you need further adjustments! 🚀
