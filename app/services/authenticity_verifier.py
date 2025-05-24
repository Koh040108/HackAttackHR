from typing import Dict, List, Any
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import IsolationForest
import numpy as np
import re
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json

class AuthenticityVerifier:
    def __init__(self):
        # Load spaCy model for NLP tasks
        self.nlp = spacy.load("en_core_web_lg")
        
        # Initialize anomaly detection model
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 3),
            max_features=5000
        )
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for fake applications
        self.suspicious_patterns = {
            'generic_phrases': [
                r'i am a highly motivated',
                r'i am seeking a challenging position',
                r'i am a team player',
                r'i am a quick learner',
                r'i am a hard worker',
                r'i am a detail-oriented',
                r'i am a results-driven',
                r'i am a self-starter'
            ],
            'inconsistent_dates': [
                r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}\b'
            ],
            'unrealistic_achievements': [
                r'increased (?:sales|revenue|efficiency) by \d{2,3}%',
                r'reduced (?:costs|time|errors) by \d{2,3}%',
                r'managed (?:team|project|budget) of \$\d+M'
            ]
        }
        
        # Weights for different verification components
        self.weights = {
            'pattern_analysis': 0.3,
            'consistency_check': 0.2,
            'anomaly_detection': 0.3,
            'external_verification': 0.2
        }

    async def verify_candidate(self, candidate_data: Dict[str, Any]) -> float:
        """Verify the authenticity of a candidate's application"""
        try:
            # Perform different verification checks
            pattern_score = self._analyze_patterns(candidate_data)
            consistency_score = self._check_consistency(candidate_data)
            anomaly_score = self._detect_anomalies(candidate_data)
            external_score = await self._verify_external_sources(candidate_data)
            
            # Calculate overall authenticity score
            authenticity_score = (
                pattern_score * self.weights['pattern_analysis'] +
                consistency_score * self.weights['consistency_check'] +
                anomaly_score * self.weights['anomaly_detection'] +
                external_score * self.weights['external_verification']
            )
            
            return float(authenticity_score)
            
        except Exception as e:
            self.logger.error(f"Error verifying candidate: {str(e)}")
            raise

    def _analyze_patterns(self, candidate_data: Dict[str, Any]) -> float:
        """Analyze text for suspicious patterns"""
        text = candidate_data.get('raw_text', '')
        experience_text = ' '.join(str(exp) for exp in candidate_data.get('experience', []))
        education_text = ' '.join(str(edu) for edu in candidate_data.get('education', []))
        
        full_text = f"{text} {experience_text} {education_text}".lower()
        
        # Count suspicious patterns
        pattern_matches = 0
        total_patterns = 0
        
        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                total_patterns += 1
                if re.search(pattern, full_text, re.IGNORECASE):
                    pattern_matches += 1
        
        # Calculate score (fewer matches = higher score)
        if total_patterns == 0:
            return 1.0
            
        return 1.0 - (pattern_matches / total_patterns)

    def _check_consistency(self, candidate_data: Dict[str, Any]) -> float:
        """Check for consistency in candidate information"""
        consistency_issues = 0
        total_checks = 0
        
        # Check experience dates
        experience = candidate_data.get('experience', [])
        if experience:
            total_checks += 1
            dates = []
            for exp in experience:
                if exp.get('start_date'):
                    dates.append(exp['start_date'])
                if exp.get('end_date') and exp['end_date'] != 'Present':
                    dates.append(exp['end_date'])
            
            # Check for overlapping dates
            if len(dates) >= 2:
                dates.sort()
                for i in range(len(dates) - 1):
                    if dates[i] == dates[i + 1]:
                        consistency_issues += 1
        
        # Check education dates
        education = candidate_data.get('education', [])
        if education:
            total_checks += 1
            dates = []
            for edu in education:
                if edu.get('start_date'):
                    dates.append(edu['start_date'])
                if edu.get('end_date') and edu['end_date'] != 'Present':
                    dates.append(edu['end_date'])
            
            # Check for overlapping dates
            if len(dates) >= 2:
                dates.sort()
                for i in range(len(dates) - 1):
                    if dates[i] == dates[i + 1]:
                        consistency_issues += 1
        
        # Check for unrealistic experience duration
        if experience:
            total_checks += 1
            for exp in experience:
                if exp.get('start_date') and exp.get('end_date'):
                    if exp['end_date'] != 'Present':
                        # TODO: Implement proper date parsing and duration calculation
                        consistency_issues += 0  # Placeholder
        
        if total_checks == 0:
            return 1.0
            
        return 1.0 - (consistency_issues / total_checks)

    def _detect_anomalies(self, candidate_data: Dict[str, Any]) -> float:
        """Detect anomalies in the application using machine learning"""
        try:
            # Prepare text features
            texts = [
                candidate_data.get('raw_text', ''),
                ' '.join(str(exp) for exp in candidate_data.get('experience', [])),
                ' '.join(str(edu) for edu in candidate_data.get('education', []))
            ]
            
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Detect anomalies
            # Note: In a real system, this would be trained on a large dataset of verified applications
            anomaly_scores = self.anomaly_detector.fit_predict(tfidf_matrix.toarray())
            
            # Convert anomaly scores to a 0-1 score (1 = normal, 0 = anomalous)
            normal_count = np.sum(anomaly_scores == 1)
            return float(normal_count / len(anomaly_scores))
            
        except Exception as e:
            self.logger.warning(f"Error in anomaly detection: {str(e)}")
            return 0.5

    async def _verify_external_sources(self, candidate_data: Dict[str, Any]) -> float:
        """Verify candidate information against external sources"""
        try:
            verification_score = 0.0
            total_checks = 0
            
            # Verify email domain
            if candidate_data.get('basic_info', {}).get('email'):
                total_checks += 1
                email = candidate_data['basic_info']['email']
                domain = email.split('@')[-1]
                
                # Check if domain is a common free email provider
                free_email_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'}
                if domain not in free_email_domains:
                    verification_score += 1
            
            # Verify LinkedIn profile (if provided)
            # TODO: Implement LinkedIn API integration
            
            # Verify education institutions
            education = candidate_data.get('education', [])
            if education:
                total_checks += 1
                # TODO: Implement education verification against a database of institutions
            
            # Verify work experience
            experience = candidate_data.get('experience', [])
            if experience:
                total_checks += 1
                # TODO: Implement company verification against a business database
            
            if total_checks == 0:
                return 0.5  # Neutral score if no external verification possible
                
            return verification_score / total_checks
            
        except Exception as e:
            self.logger.warning(f"Error in external verification: {str(e)}")
            return 0.5 