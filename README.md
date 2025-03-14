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

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_trf
python -m nltk.downloader punkt wordnet stopwords
```

4. Download the ESCO skills dataset and place it in the `data/` directory:
```bash
mkdir -p data
wget -O data/esco_skills.csv https://esco.ec.europa.eu/sites/default/files/esco_skills.csv
```

## Usage

### Run the API server:
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at:
- Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Endpoint: [http://127.0.0.1:8000/upload](http://127.0.0.1:8000/upload)

### Example API Request:
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/upload/' \
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
│   ├── models.py            # ML models handling
│   ├── __init__.py
├── data/
│   └── esco_skills.csv      # ESCO skills database
├── models/                  # Saved ML models
├── notebooks/               # Jupyter notebooks for experimentation
├── frontend/                # (Future) Web interface
├── requirements.txt         # Dependency list
├── .env                     # Environment variables (if needed)
└── README.md                # This document
```

## API Documentation

### POST /upload/
Upload a resume file (PDF/DOCX) and get parsed data with job matches.

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
      "similarity_score": 0.95
    }
  ]
}
```

## Troubleshooting

- **Check the correct URL:** If running the server locally, use [http://127.0.0.1:8000](http://127.0.0.1:8000) instead of [http://0.0.0.0:8000](http://0.0.0.0:8000).
- **Ensure you are in the correct path:** Before running commands, navigate to the project directory.

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
📧 abdullahshareef7945512@gmail.com  
🔗 [GitHub Repository](https://github.com/AbdullahShareef79/resume-parser-job-matcher)

