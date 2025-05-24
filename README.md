# AI-Powered Talent Acquisition System

An intelligent system for automating and enhancing the talent acquisition process using artificial intelligence and machine learning.

## Features

- **Resume Parsing & Analysis**: Automated extraction and analysis of candidate information from resumes and cover letters
- **Candidate Screening**: AI-powered screening of candidates based on job requirements and company culture
- **Authenticity Verification**: Detection of fake applications and verification of candidate information
- **Skill Gap Analysis**: Analysis of candidate skills against job requirements
- **Campus Recruitment Support**: Specialized tools for handling campus recruitment processes

## Project Structure

```
hackattackhr/
├── app/
│   ├── api/                 # API endpoints
│   ├── core/               # Core business logic
│   ├── models/             # Database models
│   ├── services/           # Business services
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## Setup and Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required NLP models:
```bash
python -m spacy download en_core_web_lg
python -m nltk.downloader punkt stopwords wordnet
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```
DATABASE_URL=sqlite:///./talent_acquisition.db
SECRET_KEY=your-secret-key
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Key Components

### 1. Resume Parser
- Extracts structured information from resumes (PDF, DOCX)
- Identifies skills, experience, education, and other relevant information
- Supports multiple document formats and languages

### 2. Candidate Screening
- Matches candidate profiles against job requirements
- Uses NLP to analyze job descriptions and candidate qualifications
- Implements scoring algorithms for candidate ranking

### 3. Authenticity Verification
- Detects potential fake or AI-generated applications
- Cross-references candidate information with external sources
- Implements anomaly detection for suspicious applications

### 4. Skill Gap Analysis
- Analyzes required vs. possessed skills
- Provides insights for training and development
- Supports workforce planning

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 