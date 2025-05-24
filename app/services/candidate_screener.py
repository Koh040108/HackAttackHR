from typing import Dict, List, Any
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging
from datetime import datetime

class CandidateScreener:
    def __init__(self):
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize TF-IDF vectorizer for text similarity
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Weights for different scoring components
        self.weights = {
            'skill_match': 0.4,
            'experience_match': 0.3,
            'education_match': 0.2,
            'cultural_fit': 0.1
        }

    async def screen_candidate(
        self,
        candidate_id: int,
        job_id: int,
        candidate_data: Dict[str, Any] = None,
        job_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Screen a candidate against job requirements"""
        try:
            # TODO: Fetch candidate and job data from database if not provided
            if not candidate_data or not job_data:
                raise ValueError("Candidate and job data must be provided")
            
            # Calculate different match scores
            skill_score = self._calculate_skill_match(
                candidate_data['skills'],
                job_data['required_skills']
            )
            
            experience_score = self._calculate_experience_match(
                candidate_data['experience'],
                job_data['experience_level']
            )
            
            education_score = self._calculate_education_match(
                candidate_data['education'],
                job_data.get('education_requirements', {})
            )
            
            cultural_fit_score = self._calculate_cultural_fit(
                candidate_data,
                job_data.get('company_culture', {})
            )
            
            # Calculate overall match score
            overall_score = (
                skill_score * self.weights['skill_match'] +
                experience_score * self.weights['experience_match'] +
                education_score * self.weights['education_match'] +
                cultural_fit_score * self.weights['cultural_fit']
            )
            
            # Identify skill gaps
            skill_gaps = self._identify_skill_gaps(
                candidate_data['skills'],
                job_data['required_skills']
            )
            
            return {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "match_score": float(overall_score),
                "component_scores": {
                    "skill_match": float(skill_score),
                    "experience_match": float(experience_score),
                    "education_match": float(education_score),
                    "cultural_fit": float(cultural_fit_score)
                },
                "skill_gaps": skill_gaps,
                "screening_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error screening candidate: {str(e)}")
            raise

    def _calculate_skill_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str]
    ) -> float:
        """Calculate how well candidate skills match required skills"""
        if not required_skills:
            return 1.0
            
        # Convert skills to lowercase for comparison
        candidate_skills = [skill.lower() for skill in candidate_skills]
        required_skills = [skill.lower() for skill in required_skills]
        
        # Calculate Jaccard similarity
        candidate_set = set(candidate_skills)
        required_set = set(required_skills)
        
        if not required_set:
            return 1.0
            
        intersection = len(candidate_set.intersection(required_set))
        union = len(candidate_set.union(required_set))
        
        return intersection / union if union > 0 else 0.0

    def _calculate_experience_match(
        self,
        experience: List[Dict[str, Any]],
        required_level: str
    ) -> float:
        """Calculate experience match score"""
        if not experience:
            return 0.0
            
        # Define experience level weights
        level_weights = {
            'entry': 1,
            'junior': 2,
            'mid': 3,
            'senior': 4,
            'lead': 5,
            'executive': 6
        }
        
        # Calculate total years of experience
        total_years = 0
        for exp in experience:
            # TODO: Implement proper date parsing and calculation
            # This is a simplified version
            if exp.get('end_date') == 'Present':
                total_years += 1
            else:
                total_years += 0.5  # Simplified assumption
                
        # Map required level to minimum years
        required_years = {
            'entry': 0,
            'junior': 1,
            'mid': 3,
            'senior': 5,
            'lead': 7,
            'executive': 10
        }.get(required_level.lower(), 0)
        
        # Calculate score based on experience ratio
        if required_years == 0:
            return 1.0
            
        score = min(total_years / required_years, 1.0)
        return score

    def _calculate_education_match(
        self,
        education: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> float:
        """Calculate education match score"""
        if not education:
            return 0.0
            
        # Define education level weights
        education_weights = {
            'high school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        # Get highest education level
        highest_level = 0
        for edu in education:
            text = edu.get('text', '').lower()
            for level, weight in education_weights.items():
                if level in text:
                    highest_level = max(highest_level, weight)
                    
        # Calculate score based on required education level
        required_level = education_weights.get(
            requirements.get('minimum_degree', 'bachelor').lower(),
            3
        )
        
        return min(highest_level / required_level, 1.0)

    def _calculate_cultural_fit(
        self,
        candidate_data: Dict[str, Any],
        company_culture: Dict[str, Any]
    ) -> float:
        """Calculate cultural fit score"""
        if not company_culture:
            return 0.5  # Neutral score if no culture data
            
        # Extract relevant text for analysis
        candidate_text = ' '.join([
            candidate_data.get('raw_text', ''),
            ' '.join(candidate_data.get('experience', [])),
            ' '.join(candidate_data.get('education', []))
        ])
        
        # Vectorize texts
        texts = [candidate_text, company_culture.get('description', '')]
        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            self.logger.warning(f"Error calculating cultural fit: {str(e)}")
            return 0.5

    def _identify_skill_gaps(
        self,
        candidate_skills: List[str],
        required_skills: List[str]
    ) -> List[str]:
        """Identify skills that the candidate is missing"""
        candidate_set = set(skill.lower() for skill in candidate_skills)
        required_set = set(skill.lower() for skill in required_skills)
        
        return list(required_set - candidate_set) 