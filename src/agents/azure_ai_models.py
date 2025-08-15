import asyncio
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
import re
import json
import logging
from .base_agent import JobData

class AzureAIModels:
    """Azure AI Services integration for job search intelligence"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Azure AI Services configuration
        self.azure_services = {
            "openai": {
                "name": "Azure OpenAI",
                "endpoint": config.get("azure_openai_endpoint", "https://your-resource.openai.azure.com"),
                "api_key": config.get("azure_openai_api_key"),
                "deployment_name": config.get("azure_openai_deployment", "gpt-4"),
                "enabled": True
            },
            "cognitive_services": {
                "name": "Azure Cognitive Services",
                "endpoint": config.get("azure_cognitive_endpoint", "https://your-resource.cognitiveservices.azure.com"),
                "api_key": config.get("azure_cognitive_api_key"),
                "enabled": True
            },
            "machine_learning": {
                "name": "Azure Machine Learning",
                "endpoint": config.get("azure_ml_endpoint", "https://your-workspace.azureml.net"),
                "api_key": config.get("azure_ml_api_key"),
                "enabled": True
            }
        }
        
        # Fallback to local models if Azure services not configured
        self.local_models = {
            "llama2": {
                "name": "Llama 2 (Local)",
                "endpoint": "http://llama2-service:8080/generate",
                "enabled": config.get("enable_local_models", False)
            },
            "falcon": {
                "name": "Falcon (Local)", 
                "endpoint": "http://falcon-service:8080/generate",
                "enabled": config.get("enable_local_models", False)
            },
            "mistral": {
                "name": "Mistral (Local)",
                "endpoint": "http://mistral-service:8080/generate", 
                "enabled": config.get("enable_local_models", False)
            }
        }
    
    async def extract_contact_info_azure(self, job_description: str, company_website: str) -> Dict[str, Any]:
        """Extract contact info using Azure AI Services + web scraping"""
        
        # First, try web scraping for contact information
        scraped_info = await self._scrape_contact_info(company_website)
        
        # Then use Azure AI to enhance and validate
        azure_enhanced_info = await self._enhance_with_azure_ai(job_description, scraped_info)
        
        return azure_enhanced_info
    
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
    
    async def _enhance_with_azure_ai(self, job_description: str, scraped_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance scraped info using Azure AI Services"""
        
        if not job_description:
            return scraped_info
        
        # Create prompt for Azure AI
        prompt = self._create_azure_enhancement_prompt(job_description, scraped_info)
        
        # Try Azure OpenAI first, then fallback to other services
        azure_result = await self._call_azure_openai(prompt)
        
        if azure_result:
            enhanced_info = self._parse_azure_response(azure_result)
            return self._combine_azure_and_scraped(scraped_info, enhanced_info)
        
        # Fallback to local models if Azure fails
        local_result = await self._enhance_with_local_models(prompt)
        if local_result:
            enhanced_info = self._parse_local_response(local_result)
            return self._combine_azure_and_scraped(scraped_info, enhanced_info)
        
        return scraped_info
    
    def _create_azure_enhancement_prompt(self, job_description: str, scraped_info: Dict[str, Any]) -> str:
        """Create prompt for Azure AI enhancement"""
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
    
    async def _call_azure_openai(self, prompt: str) -> Dict[str, Any]:
        """Call Azure OpenAI service"""
        try:
            openai_config = self.azure_services["openai"]
            if not openai_config["enabled"] or not openai_config["api_key"]:
                return None
            
            headers = {
                "api-key": openai_config["api_key"],
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "You are an AI assistant that extracts and enhances contact information from job postings."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 300,
                "temperature": 0.1
            }
            
            url = f"{openai_config['endpoint']}/openai/deployments/{openai_config['deployment_name']}/chat/completions?api-version=2024-02-15-preview"
            
            response = await asyncio.to_thread(
                requests.post, url, headers=headers, json=payload, timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "service": "azure_openai",
                    "response": result
                }
            else:
                self.logger.warning(f"Azure OpenAI failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Azure OpenAI call failed: {e}")
            return None
    
    def _parse_azure_response(self, azure_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Azure AI response"""
        try:
            if azure_result.get("status") == "success":
                response = azure_result.get("response", {})
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    return self._fallback_enhancement_parsing(content)
            else:
                return self._fallback_enhancement_parsing("")
                
        except Exception as e:
            self.logger.warning(f"Failed to parse Azure response: {e}")
            return self._fallback_enhancement_parsing("")
    
    async def _enhance_with_local_models(self, prompt: str) -> List[Dict[str, Any]]:
        """Fallback to local models if Azure fails"""
        tasks = []
        
        for model_name, model_config in self.local_models.items():
            if model_config["enabled"]:
                task = self._enhance_with_local_model(model_name, model_config, prompt)
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            valid_results = []
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    valid_results.append(result)
            
            return valid_results
        
        return []
    
    async def _enhance_with_local_model(self, model_name: str, model_config: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Enhance using a local model"""
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
                return {
                    "status": "success",
                    "model": model_name,
                    "response": result
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
    
    def _parse_local_response(self, local_result: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse local model response"""
        if not local_result:
            return self._fallback_enhancement_parsing("")
        
        # Use the first successful result
        for result in local_result:
            if result.get("status") == "success":
                response_text = result.get("response", {}).get("generated_text", "")
                return self._fallback_enhancement_parsing(response_text)
        
        return self._fallback_enhancement_parsing("")
    
    def _fallback_enhancement_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for AI enhancement"""
        return {
            "contact_person": "Not found",
            "contact_email": "Not found",
            "contact_phone": "Not found",
            "linkedin_url": "Not found",
            "confidence_score": 50
        }
    
    def _combine_azure_and_scraped(self, scraped_info: Dict[str, Any], enhanced_info: Dict[str, Any]) -> Dict[str, Any]:
        """Combine Azure AI enhancements with scraped information"""
        final_info = scraped_info.copy()
        
        if not enhanced_info:
            return final_info
        
        # Update fields if AI found better information
        for field in ["contact_person", "contact_email", "contact_phone", "linkedin_url"]:
            ai_value = enhanced_info.get(field)
            if ai_value and ai_value != "Not found" and final_info.get(field) == "Not found":
                final_info[field] = ai_value
        
        # Add confidence score
        if enhanced_info.get("confidence_score"):
            final_info["ai_confidence"] = enhanced_info["confidence_score"]
        
        return final_info
    
    async def make_decision_azure(self, job_data: JobData, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Make decision using Azure AI Services"""
        
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
        
        # Try Azure OpenAI first
        azure_result = await self._call_azure_openai(decision_prompt)
        
        if azure_result:
            decision = self._parse_azure_decision(azure_result)
            return decision
        
        # Fallback to local models
        local_result = await self._enhance_with_local_models(decision_prompt)
        if local_result:
            decision = self._parse_local_decision(local_result)
            return decision
        
        # Default decision
        return {
            "decision": "add",
            "reason": "Default decision due to service unavailability",
            "confidence": 30
        }
    
    def _parse_azure_decision(self, azure_result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Azure AI decision response"""
        try:
            if azure_result.get("status") == "success":
                response = azure_result.get("response", {})
                content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                
                if json_match:
                    json_str = json_match.group()
                    return json.loads(json_str)
                else:
                    return self._fallback_decision_parsing(content)
            else:
                return self._fallback_decision_parsing("")
                
        except Exception as e:
            self.logger.warning(f"Failed to parse Azure decision: {e}")
            return self._fallback_decision_parsing("")
    
    def _parse_local_decision(self, local_result: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse local model decision response"""
        if not local_result:
            return self._fallback_decision_parsing("")
        
        # Use the first successful result
        for result in local_result:
            if result.get("status") == "success":
                response_text = result.get("response", {}).get("generated_text", "")
                return self._fallback_decision_parsing(response_text)
        
        return self._fallback_decision_parsing("")
    
    def _fallback_decision_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing for decision response"""
        return {
            "decision": "add",
            "reason": "Default decision due to parsing failure",
            "confidence": 50
        }
