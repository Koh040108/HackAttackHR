import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import Base, engine, SessionLocal
from app.services.resume_parser import ResumeParser
from app.services.candidate_screener import CandidateScreener
from app.services.authenticity_verifier import AuthenticityVerifier
import json
from datetime import datetime

# Create test client
client = TestClient(app)

# Sample test data
SAMPLE_JOB_POSTING = {
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer...",
    "required_skills": ["python", "django", "sql", "aws"],
    "experience_level": "senior",
    "location": "New York",
    "department": "Engineering"
}

SAMPLE_CANDIDATE_DATA = {
    "basic_info": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "123-456-7890"
    },
    "skills": ["python", "django", "postgresql", "docker"],
    "experience": [
        {
            "text": "Senior Developer at Tech Corp",
            "start_date": "Jan 2020",
            "end_date": "Present"
        }
    ],
    "education": [
        {
            "text": "Bachelor of Science in Computer Science",
            "start_date": "Sep 2015",
            "end_date": "May 2019"
        }
    ]
}

@pytest.fixture(scope="session")
def db():
    # Create test database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_job_posting():
    response = client.post("/jobs/", json=SAMPLE_JOB_POSTING)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == SAMPLE_JOB_POSTING["title"]
    assert data["required_skills"] == SAMPLE_JOB_POSTING["required_skills"]

def test_resume_parser():
    parser = ResumeParser()
    # Create a mock resume file
    resume_text = """
    John Doe
    john.doe@example.com
    123-456-7890
    
    Skills:
    - Python
    - Django
    - PostgreSQL
    - Docker
    
    Experience:
    Senior Developer at Tech Corp
    Jan 2020 - Present
    
    Education:
    Bachelor of Science in Computer Science
    Sep 2015 - May 2019
    """
    
    # Test parsing (in a real test, we would create an actual file)
    # This is a simplified test
    parsed_data = parser._extract_basic_info(resume_text)
    assert parsed_data["name"] == "John Doe"
    assert parsed_data["email"] == "john.doe@example.com"
    assert parsed_data["phone"] == "123-456-7890"

def test_candidate_screener():
    screener = CandidateScreener()
    
    # Test skill matching
    skill_score = screener._calculate_skill_match(
        SAMPLE_CANDIDATE_DATA["skills"],
        SAMPLE_JOB_POSTING["required_skills"]
    )
    assert 0 <= skill_score <= 1
    
    # Test experience matching
    experience_score = screener._calculate_experience_match(
        SAMPLE_CANDIDATE_DATA["experience"],
        SAMPLE_JOB_POSTING["experience_level"]
    )
    assert 0 <= experience_score <= 1

def test_authenticity_verifier():
    verifier = AuthenticityVerifier()
    
    # Test pattern analysis
    pattern_score = verifier._analyze_patterns(SAMPLE_CANDIDATE_DATA)
    assert 0 <= pattern_score <= 1
    
    # Test consistency check
    consistency_score = verifier._check_consistency(SAMPLE_CANDIDATE_DATA)
    assert 0 <= consistency_score <= 1

def test_end_to_end_screening():
    # Create a job posting
    job_response = client.post("/jobs/", json=SAMPLE_JOB_POSTING)
    job_id = job_response.json()["id"]
    
    # Create a candidate application
    candidate_response = client.post(
        "/candidates/upload-resume",
        files={"file": ("resume.txt", "Sample resume content")},
        data={"job_id": job_id}
    )
    assert candidate_response.status_code == 200
    
    # Test screening
    screening_response = client.post(
        f"/screening/analyze",
        params={"candidate_id": 1, "job_id": job_id}
    )
    assert screening_response.status_code == 200
    screening_data = screening_response.json()
    assert "match_score" in screening_data
    assert "authenticity_score" in screening_data
    assert "skill_gaps" in screening_data

def test_skill_gap_analysis():
    response = client.get(
        "/candidates/1/skill-gap",
        params={"job_id": 1}
    )
    assert response.status_code == 200
    data = response.json()
    assert "missing_skills" in data
    assert "skill_match_percentage" in data
    assert 0 <= data["skill_match_percentage"] <= 100

if __name__ == "__main__":
    pytest.main([__file__]) 