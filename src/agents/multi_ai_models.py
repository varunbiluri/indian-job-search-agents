import asyncio
from typing import List, Dict, Any
from datetime import datetime
import requests
import json
from .base_agent import JobData

class MultiAIModelsAgent(BaseSearchAgent):
    """Agent using multiple open-source AI models for decision making"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("MultiAIModelsAgent", "multi_ai", config)
        self.models = self._initialize_models()
        
    def _initialize_models(self) -> Dict[str, Any]:
        """Initialize multiple open-source AI models"""
        return {
            "llama2": {
                "name": "Llama 2",
                "endpoint": config.get("llama2_endpoint", "http://llama2-service:8080/generate"),
                "enabled": True,
                "model_size": "7B",
                "max_tokens": 512
            },
            "falcon": {
                "name": "Falcon",
                "endpoint": config.get("falcon_endpoint", "http://falcon-service:8080/generate"),
                "enabled": True,
                "model_size": "7B",
                "max_tokens": 512
            },
            "mistral": {
                "name": "Mistral",
                "endpoint": config.get("mistral_endpoint", "http://mistral-service:8080/generate"),
                "enabled": True,
                "model_size": "7B",
                "max_tokens": 512
            }
        }
    
    async def search_jobs(self, job_role: str, location: str = None, keywords: List[str] = None) -> List[JobData]:
        """This agent doesn't search for jobs, it enhances existing ones"""
        return []
    
    async def extract_contact_info(self, job_data: JobData) -> JobData:
        """Extract contact information using multiple AI models"""
        if not job_data.job_description:
            return job_data
        
        # Use multiple AI models for better accuracy
        ai_results = await self._run_multi_ai_extraction(job_data)
        
        # Combine results using voting mechanism
        final_result = self._combine_ai_results(ai_results)
        
        # Update job data
        job_data.contact_person = final_result.get("contact_person", "Not found")
        job_data.contact_email = final_result.get("contact_email", "Not found")
        job_data.contact_phone = final_result.get("contact_phone", "Not found")
        job_data.linkedin_url = final_result.get("linkedin_url", "Not found")
        job_data.confidence_score = final_result.get("confidence_score", job_data.confidence_score)
        
        return job_data
    
    async def _run_multi_ai_extraction(self, job_data: JobData) -> List[Dict[str, Any]]:
        """Run contact extraction using multiple AI models"""
        tasks = []
        
        for model_name, model_config in self.models.items():
            if model_config["enabled"]:
                task = self._extract_with_model(model_name, model_config, job_data)
                tasks.append(task)
        
        # Run all models in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed extractions
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get("status") == "success":
                valid_results.append(result)
        
        return valid_results
    
    async def _extract_with_model(self, model_name: str, model_config: Dict[str, Any], job_data: JobData) -> Dict[str, Any]:
        """Extract contact information using a specific AI model"""
        try:
            prompt = self._create_extraction_prompt(job_data)
            
            # Call the AI model endpoint
            response = await asyncio.to_thread(
                requests.post,
                model_config["endpoint"],
                json={
                    "prompt": prompt,
                    "max_tokens": model_config["max_tokens"],
                    "temperature": 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_info = self._parse_ai_response(result.get("generated_text", ""))
                
                return {
                    "status": "success",
                    "model": model_name,
                    "extracted_info": extracted_info,
                    "confidence": result.get("confidence", 0.7)
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
    
    def _create_extraction_prompt(self, job_data: JobData) -> str:
        """Create prompt for AI models"""
        return f"""
        Extract contact information from this job posting:
        
        Job Title: {job_data.job_title}
        Company: {job_data.company_name}
        Description: {job_data.job_description[:1000]}
        
        Please extract and return ONLY the following information in JSON format:
        {{
            "contact_person": "Name of contact person if mentioned",
            "contact_email": "Email address if mentioned",
            "contact_phone": "Phone number if mentioned",
            "linkedin_url": "LinkedIn profile URL if mentioned",
            "confidence_score": "Confidence level 0-100"
        }}
        
        If information is not found, use "Not found" as the value.
        """
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI model response"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            else:
                # Fallback parsing
                return self._fallback_parsing(response_text)
                
        except Exception as e:
            self.logger.warning(f"Failed to parse AI response: {e}")
            return self._fallback_parsing(response_text)
    
    def _fallback_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        result = {
            "contact_person": "Not found",
            "contact_email": "Not found",
            "contact_phone": "Not found",
            "linkedin_url": "Not found",
            "confidence_score": 50
        }
        
        # Simple regex-based extraction
        import re
        
        # Extract email
        email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response_text)
        if email_match:
            result["contact_email"] = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'[\+]?[1-9][\d]{0,15}', response_text)
        if phone_match:
            result["contact_phone"] = phone_match.group()
        
        # Extract LinkedIn URL
        linkedin_match = re.search(r'https?://[^\s]*linkedin\.com[^\s]*', response_text)
        if linkedin_match:
            result["linkedin_url"] = linkedin_match.group()
        
        return result
    
    def _combine_ai_results(self, ai_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine results from multiple AI models using voting mechanism"""
        if not ai_results:
            return {
                "contact_person": "Not found",
                "contact_email": "Not found",
                "contact_phone": "Not found",
                "linkedin_url": "Not found",
                "confidence_score": 0
            }
        
        # Count votes for each field
        field_votes = {
            "contact_person": {},
            "contact_email": {},
            "contact_phone": {},
            "linkedin_url": {}
        }
        
        total_confidence = 0
        
        for result in ai_results:
            extracted = result.get("extracted_info", {})
            confidence = result.get("confidence", 0.5)
            total_confidence += confidence
            
            for field in field_votes:
                value = extracted.get(field, "Not found")
                if value != "Not found":
                    if value not in field_votes[field]:
                        field_votes[field][value] = 0
                    field_votes[field][value] += confidence
        
        # Select most voted values
        final_result = {}
        for field, votes in field_votes.items():
            if votes:
                # Get value with highest weighted votes
                best_value = max(votes.items(), key=lambda x: x[1])[0]
                final_result[field] = best_value
            else:
                final_result[field] = "Not found"
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(ai_results) if ai_results else 0
        final_result["confidence_score"] = int(avg_confidence * 100)
        
        return final_result
    
    async def make_decision(self, job_data: JobData, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI models to make decision about adding job to database"""
        
        decision_prompt = f"""
        Should this job be added to the database based on user preferences?
        
        Job: {job_data.job_title} at {job_data.company_name}
        Location: {job_data.location}
        Salary: {job_data.salary_range or 'Not specified'}
        Requirements: {job_data.requirements or 'Not specified'}
        
        User Preferences:
        - Preferred locations: {user_preferences.get('locations', [])}
        - Salary range: {user_preferences.get('salary_range', 'Any')}
        - Skills: {user_preferences.get('skills', [])}
        - Experience level: {user_preferences.get('experience_level', 'Any')}
        
        Return JSON: {{"decision": "add" or "reject", "reason": "explanation", "confidence": 0-100}}
        """
        
        # Get decision from all models
        decisions = await self._get_ai_decisions(decision_prompt)
        
        # Combine decisions
        final_decision = self._combine_decisions(decisions)
        
        return final_decision
    
    async def _get_ai_decisions(self, prompt: str) -> List[Dict[str, Any]]:
        """Get decisions from all AI models"""
        tasks = []
        
        for model_name, model_config in self.models.items():
            if model_config["enabled"]:
                task = self._get_decision_from_model(model_name, model_config, prompt)
                tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result.get("status") == "success":
                valid_results.append(result)
        
        return valid_results
    
    async def _get_decision_from_model(self, model_name: str, model_config: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Get decision from a specific AI model"""
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
                # Default decision
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
