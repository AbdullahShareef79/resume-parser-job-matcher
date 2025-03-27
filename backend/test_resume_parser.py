import pytest
from resume_parser import parse_resume, extract_skills, extract_name
import os

# Test Files
TEST_RESUME_PDF = 'test_resume_pdf'
TEST_RESUME_DOCX = 'test_resume_docx'

@pytest.fixture
def sample_text():
    return """
    John Doe
        Email: john.doe@example.com | Phone: (555) 123-4567
    
    SKILLS:
    Python, JavaScript, Machine Learning, AWS
    
    EXPERIENCE:
    Senior Developer at Tech Company (2020-Present)
    - Built web applications with Python and React
    - Implemented machine learning models
    """
    
def test_extract_name():
    assert extract_name(sample_text) == 'John Does'
    assert extract_name('') is None
    assert extract_name('Resume of Jane Smith') == 'Jane Smith'
    
def test_extract_skills(sample_text):
    skills = extract_skills(sample_text)
    assert "Python" in skills
    assert "JavaScript" in skills
    assert "Machine Learning" in skills
    assert "AWS" in skills
    assert "Ruby" not in skills  # Shouldn't be present

def test_parse_resume_pdf():
    if os.path.exists(TEST_RESUME_PDF):
        result = parse_resume(TEST_RESUME_PDF)
        assert isinstance(result, dict)
        assert "skills" in result
        assert "name" in result
    else:
        pytest.skip("Test PDF resume not found")

def test_parse_resume_docx():
    if os.path.exists(TEST_RESUME_DOCX):
        result = parse_resume(TEST_RESUME_DOCX)
        assert isinstance(result, dict)
        assert "skills" in result
        assert "name" in result
    else:
        pytest.skip("Test DOCX resume not found")