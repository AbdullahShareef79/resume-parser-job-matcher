import pytest
from resume_parser import parse_resume, extract_skills, extract_name
import os

# Test Files
TEST_RESUME_PDF = 'test_resume_pdf'
TEST_RESUME_DOCX = 'test_resume_docx'

@pytest.fixture
def sample_pdf_path():
    return "test_resumes/sample.pdf"
    

def test_parse_resume(sample_pdf_path):
    result = parse_resume(sample_pdf_path)
    assert isinstance(result, dict)
    assert "skills" in result
    
def test_parse_resume_docx():
    if os.path.exists(TEST_RESUME_DOCX):
        result = parse_resume(TEST_RESUME_DOCX)
        assert isinstance(result, dict)
        assert "skills" in result
        assert "name" in result
    else:
        pytest.skip("Test DOCX resume not found")