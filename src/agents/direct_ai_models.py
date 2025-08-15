import asyncio
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from .base_agent import JobData

class DirectAIModels:
    """Direct AI model inference without external APIs"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Direct model endpoints (local deployment)
        self.models = {
            "llama2": {
                "name": "Llama 2",
                "endpoint": "http://llama2-service:8080/generate",
                "enabled": True
            },
            "falcon": {
                "name": "Falcon", 
                "endpoint": "http://falcon-service:8080/generate",
                "enabled": True
            },
            "mistral": {
                "name": "Mistral",
                "endpoint": "http://mistral-service:8080/generate", 
                "enabled": True
            }
        }
    
    async def extract_contact_info_direct(self, job_description: str, company_website: str) -> Dict[str, Any]:
        """Extract contact info using direct AI model inference + web scraping"""
        
        # First, try web scraping for contact information
        scraped_info = await self._scrape_contact_info(company_website)
        
        # Then use AI models to enhance and validate
        ai_enhanced_info = await self._enhance_with_ai_models(job_description, scraped_info)
        
        return ai_enhanced_info
    
    async def _scrape_contact_info(self, website_url: str) -> Dict[str, Any]:
        """Direct web scraping for contact information"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = await asyncio.to_thread(
                requests.get, website_url, headers=headers, timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract contact information using multiple strategies
                contact_info = {
                    "contact_person": "Not found",
                    "contact_email": "Not found", 
                    "contact_phone": "Not found",
                    "linkedin_url": "Not found",
                    "hr_email": "Not found"
                }
                
                # Extract emails
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, response.text)
                if emails:
                    # Filter for HR/career emails
                    hr_emails = [email for email in emails if any(keyword in email.lower() 
                                                               for keyword in ['hr', 'career', 'jobs', 'recruit', 'talent'])]
                    if hr_emails:
                        contact_info["hr_email"] = hr_emails[0]
                        contact_info["contact_email"] = hr_emails[0]
                    else:
                        contact_info["contact_email"] = emails[0]
                
                # Extract phone numbers
                phone_pattern = r'[\+]?[1-9][\d]{0,15}'
                phones = re.findall(phone_pattern, response.text)
                if phones:
                    contact_info["contact_phone"] = phones[0]
                
                # Extract LinkedIn URLs
                linkedin_pattern = r'https?://[^\s]*linkedin\.com[^\s]*'
                linkedin_urls = re.findall(linkedin_pattern, response.text)
                if linkedin_urls:
                    contact_info["linkedin_url"] = linkedin_urls[0]
                
                # Look for contact person names
                contact_person_patterns = [
                    r'Contact:\s*([A-Z][a-z]+ [A-Z][a-z]+)',
                    r'HR:\s*([A-Z][a-z]+ [A-Z][a-z]+)',
                    r'([A-Z][a-z]+ [A-Z][a-z]+)\s*HR',
                    r'([A-Z][a-z]+ [A-Z][a-z]+)\s*Manager'
                ]
                
                for pattern in contact_person_patterns:
                    matches = re.findall(pattern, response.text)
                    if matches:
                        contact_info["contact_person"] = matches[0]
                        break
                
                return contact_info
                
        except Exception as e:
            self.logger.warning(f"Web scraping failed for {website_url}: {e}")
        
        return {
            "contact_person": "Not found",
            "contact_email": "Not found",
            "contact_phone": "Not found", 
            "linkedin_url": "Not found",
            "hr_email": "Not found"
        }
    
    async def _enhance_with_ai_models(self, job_description: str, scraped_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance scraped info using direct AI model inference"""
        
        if not job_description:
            return scraped_info
        
        # Create prompt for AI models
        prompt = self._create_enhancement_prompt(job_description, scraped_info)
        
        # Get results from all AI models
        ai_results = await self._get_ai_enhancements(prompt)
        
        # Combine AI results with scraped info
        enhanced_info = self._combine_ai_and_scraped(scraped_info, ai_results)
        
        return enhanced_info
    
    def _create_enhancement_prompt(self, job_description: str, scraped_info: Dict[str, Any]) -> str:
        """Create prompt for AI model enhancement"""
        return f"""
        Enhance this contact information extracted from a job posting:
        
        Job Description: {job_description[:1000]}
        
        Current Contact Info:
        - Contact Person: {scraped_info.get('contact_person', 'Not found')}
        - Email: {scraped_info.get('contact_email', 'Not found')}
        - Phone: {scraped_info.get('contact_phone', 'Not found')}
        - LinkedIn: {scraped_info.get('linkedin_url', 'Not found')}
        
        Please enhance and return ONLY the contact information in JSON format:
        {{
            "contact_person": "Enhanced name if found",
            "contact_email": "Best email found",
            "contact_phone": "Best phone found", 
            "linkedin_url": "Best LinkedIn URL found",
            "confidence_score": "0-100"
        }}
        
        If no enhancement possible, return the original values.
        """
    
    async def _get_ai_enhancements(self, prompt: str) -> List[Dict[str, Any]]:
        """Get enhancements from all AI models directly"""
        tasks = []
        
        for model_name, model_config in self.models.items():
            if model_config["enabled"]:
                task = self._enhance_with_model(model_name, model_config, prompt)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter valid results
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    valid_results.append(result)
            
            return valid_results
        
        return []
    
    async def _enhance_with_model(self, model_name: str, model_config: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance using a specific AI model directly"""
        try:
            response = await asyncio.to_thread(
                requests.post,
                model_config["endpoint"],
                json={
                    "prompt": prompt,
                    "max_tokens": 300,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_info = self._parse_ai_enhancement(result.get("generated_text", ""))
                
                return {
                    "status": "success",
                    "model": model_name,
                    "enhanced_info": enhanced_info
                }
            else:
                return {
                    "status": "failed",
                    "model": model_name,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "model": model_name,
                "error": str(e)
            }
    
    def _parse_ai_enhancement(self, response_text: str) -> Dict[str, Any]:
        """Parse AI enhancement response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return self._fallback_enhancement_parsing(response_text)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse AI enhancement: {e}")
            return self._fallback_enhancement_parsing(response_text)
    
    def _fallback_enhancement_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for AI enhancement"""
        return {
            "contact_person": "Not found",
            "contact_email": "Not found",
            "contact_phone": "Not found",
            "linkedin_url": "Not found",
            "confidence_score": 50
        }
    
    def _combine_ai_and_scraped(self, scraped_info: Dict[str, Any], ai_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine AI enhancements with scraped information"""
        final_info = scraped_info.copy()
        
        if not ai_results:
            return final_info
        
        # Use AI to enhance scraped info
        for result in ai_results:
            enhanced = result.get("enhanced_info", {})
            
            # Update fields if AI found better information
            for field in ["contact_person", "contact_email", "contact_phone", "linkedin_url"]:
                ai_value = enhanced.get(field)
                if ai_value and ai_value != "Not found" and final_info.get(field) == "Not found":
                    final_info[field] = ai_value
        
        # Add confidence score
        if ai_results:
            confidence_scores = [result.get("enhanced_info", {}).get("confidence_score", 50) 
                               for result in ai_results]
            final_info["ai_confidence"] = sum(confidence_scores) / len(confidence_scores)
        
        return final_info
    
    async def make_decision_direct(self, job_data: JobData, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision using direct AI model inference"""
        
        decision_prompt = f"""
        Should this job be added to the database based on user preferences?
        
        Job: {job_data.job_title} at {job_data.company_name}
        Location: {job_data.location}
        Salary: {getattr(job_data, 'salary_range', 'Not specified')}
        Requirements: {getattr(job_data, 'requirements', 'Not specified')}
        
        User Preferences:
        - Preferred locations: {user_preferences.get('locations', [])}
        - Salary range: {user_preferences.get('salary_range', 'Any')}
        - Skills: {user_preferences.get('skills', [])}
        - Experience level: {user_preferences.get('experience_level', 'Any')}
        
        Return JSON: {{"decision": "add" or "reject", "reason": "explanation", "confidence": 0-100}}
        """
        
        # Get decision from all models
        decisions = await self._get_ai_decisions_direct(decision_prompt)
        
        # Combine decisions
        final_decision = self._combine_decisions(decisions)
        
        return final_decision
    
    async def _get_ai_decisions_direct(self, prompt: str) -> List[Dict[str, Any]]:
        """Get decisions from all AI models directly"""
        tasks = []
        
        for model_name, model_config in self.models.items():
            if model_config["enabled"]:
                task = self._get_decision_from_model_direct(model_name, model_config, prompt)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    valid_results.append(result)
            
            return valid_results
        
        return []
    
    async def _get_decision_from_model_direct(self, model_name: str, model_config: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Get decision from a specific AI model directly"""
        try:
            response = await asyncio.to_thread(
                requests.post,
                model_config["endpoint"],
                json={
                    "prompt": prompt,
                    "max_tokens": 200,
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                decision = self._parse_decision_response(result.get("generated_text", ""))
                
                return {
                    "status": "success",
                    "model": model_name,
                    "decision": decision
                }
            else:
                return {
                    "status": "failed",
                    "model": model_name,
                    "error": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "failed",
                "model": model_name,
                "error": str(e)
            }
    
    def _parse_decision_response(self, response_text: str) -> Dict[str, Any]:
        """Parse decision response from AI model"""
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                return {
                    "decision": "add",
                    "reason": "Default decision due to parsing failure",
                    "confidence": 50
                }
                
        except Exception as e:
            return {
                "decision": "add",
                "reason": f"Error parsing response: {e}",
                "confidence": 30
            }
    
    def _combine_decisions(self, decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine decisions from multiple AI models"""
        if not decisions:
            return {
                "decision": "add",
                "reason": "No AI models available",
                "confidence": 0
            }
        
        # Count votes for each decision
        decision_votes = {"add": 0, "reject": 0}
        total_confidence = 0
        
        for decision_data in decisions:
            decision = decision_data.get("decision", "add")
            confidence = decision_data.get("confidence", 50)
            
            decision_votes[decision] += confidence
            total_confidence += confidence
        
        # Get final decision
        final_decision = "add" if decision_votes["add"] >= decision_votes["reject"] else "reject"
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(decisions) if decisions else 0
        
        return {
            "decision": final_decision,
            "reason": f"Combined decision from {len(decisions)} AI models",
            "confidence": int(avg_confidence),
            "model_votes": decision_votes
        }
