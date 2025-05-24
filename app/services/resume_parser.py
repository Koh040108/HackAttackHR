import spacy
import PyPDF2
import docx
from typing import Dict, List, Any
from fastapi import UploadFile
import io
import re
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import logging

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ResumeParser:
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_lg")
        self.stop_words = set(stopwords.words('english'))
        
        # Common skills dictionary
        self.skills_dict = {
            'programming': ['python', 'java', 'javascript', 'c++', 'ruby', 'php', 'swift', 'kotlin'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle'],
            'frameworks': ['django', 'flask', 'react', 'angular', 'vue', 'spring', 'express'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp'],
            'soft_skills': ['leadership', 'communication', 'teamwork', 'problem-solving', 'time-management']
        }
        
        # Regular expressions for common patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'\+?1?\s*\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def parse_resume(self, file: UploadFile) -> Dict[str, Any]:
        """Parse resume file and extract relevant information"""
        try:
            # Read file content based on file type
            content = await self._read_file_content(file)
            
            # Extract basic information
            basic_info = self._extract_basic_info(content)
            
            # Extract skills
            skills = self._extract_skills(content)
            
            # Extract experience
            experience = self._extract_experience(content)
            
            # Extract education
            education = self._extract_education(content)
            
            return {
                "basic_info": basic_info,
                "skills": skills,
                "experience": experience,
                "education": education,
                "raw_text": content
            }
            
        except Exception as e:
            self.logger.error(f"Error parsing resume: {str(e)}")
            raise

    async def _read_file_content(self, file: UploadFile) -> str:
        """Read content from different file types"""
        content = await file.read()
        
        if file.filename.endswith('.pdf'):
            return self._extract_from_pdf(content)
        elif file.filename.endswith('.docx'):
            return self._extract_from_docx(content)
        elif file.filename.endswith('.txt'):
            return content.decode('utf-8')
        else:
            raise ValueError("Unsupported file format")

    def _extract_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            self.logger.error(f"Error extracting PDF content: {str(e)}")
            raise

    def _extract_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            docx_file = io.BytesIO(content)
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            self.logger.error(f"Error extracting DOCX content: {str(e)}")
            raise

    def _extract_basic_info(self, text: str) -> Dict[str, str]:
        """Extract basic information like name, email, phone"""
        doc = self.nlp(text)
        
        # Extract name (first entity of type PERSON)
        name = ""
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                break
        
        # Extract email and phone
        email = re.search(self.email_pattern, text)
        phone = re.search(self.phone_pattern, text)
        
        return {
            "name": name,
            "email": email.group(0) if email else "",
            "phone": phone.group(0) if phone else ""
        }

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        doc = self.nlp(text.lower())
        found_skills = set()
        
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        tokens = [token for token in tokens if token not in self.stop_words]
        
        # Check for skills in each category
        for category, skills in self.skills_dict.items():
            for skill in skills:
                if skill in tokens or skill in text.lower():
                    found_skills.add(skill)
        
        return list(found_skills)

    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from text"""
        # Split text into sections
        sections = text.split('\n\n')
        experience_sections = []
        
        # Look for experience-related keywords
        experience_keywords = ['experience', 'work', 'employment', 'job']
        
        for section in sections:
            if any(keyword in section.lower() for keyword in experience_keywords):
                # Extract dates using regex
                date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
                dates = re.findall(date_pattern, section)
                
                if dates:
                    experience_sections.append({
                        "text": section,
                        "start_date": dates[0] if len(dates) > 0 else "",
                        "end_date": dates[1] if len(dates) > 1 else "Present"
                    })
        
        return experience_sections

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from text"""
        # Split text into sections
        sections = text.split('\n\n')
        education_sections = []
        
        # Look for education-related keywords
        education_keywords = ['education', 'university', 'college', 'degree', 'bachelor', 'master', 'phd']
        
        for section in sections:
            if any(keyword in section.lower() for keyword in education_keywords):
                # Extract dates using regex
                date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
                dates = re.findall(date_pattern, section)
                
                if dates:
                    education_sections.append({
                        "text": section,
                        "start_date": dates[0] if len(dates) > 0 else "",
                        "end_date": dates[1] if len(dates) > 1 else "Present"
                    })
        
        return education_sections 