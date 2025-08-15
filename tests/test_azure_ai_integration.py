#!/usr/bin/env python3
"""
Test Azure AI Integration for Indian Job Search
This script tests the Azure AI services integration before deployment
"""

import asyncio
import sys
import os
import yaml
import requests
from typing import Dict, Any

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.azure_ai_models import AzureAIModels

class AzureAITester:
    """Test Azure AI integration"""
    
    def __init__(self):
        self.config = self._load_config()
        self.azure_ai = AzureAIModels(self.config)
        self.test_results = []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load Azure AI configuration"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'azure_ai_config.yaml')
        
        if not os.path.exists(config_path):
            print(f"❌ Configuration file not found: {config_path}")
            print("Please create the configuration file first.")
            return {}
        
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            return {}
    
    async def test_azure_openai_connection(self) -> bool:
        """Test Azure OpenAI connection"""
        print("🔍 Testing Azure OpenAI connection...")
        
        try:
            openai_config = self.config.get('azure_openai', {})
            if not openai_config.get('enabled'):
                print("⚠️  Azure OpenAI not enabled in config")
                return False
            
            endpoint = openai_config.get('endpoint')
            api_key = openai_config.get('api_key')
            
            if not endpoint or not api_key:
                print("❌ Azure OpenAI endpoint or API key not configured")
                return False
            
            # Test connection with a simple prompt
            test_prompt = "Hello, this is a test. Please respond with 'Test successful'."
            
            result = await self.azure_ai._call_azure_openai(test_prompt)
            
            if result and result.get('status') == 'success':
                print("✅ Azure OpenAI connection successful!")
                self.test_results.append(("Azure OpenAI", "PASS"))
                return True
            else:
                print("❌ Azure OpenAI connection failed")
                self.test_results.append(("Azure OpenAI", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Azure OpenAI test failed: {e}")
            self.test_results.append(("Azure OpenAI", "FAIL"))
            return False
    
    async def test_web_scraping(self) -> bool:
        """Test web scraping functionality"""
        print("🔍 Testing web scraping functionality...")
        
        try:
            # Test with a simple website
            test_url = "https://httpbin.org/html"
            
            scraped_info = await self.azure_ai._scrape_contact_info(test_url)
            
            if scraped_info:
                print("✅ Web scraping test successful!")
                self.test_results.append(("Web Scraping", "PASS"))
                return True
            else:
                print("❌ Web scraping test failed")
                self.test_results.append(("Web Scraping", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Web scraping test failed: {e}")
            self.test_results.append(("Web Scraping", "FAIL"))
            return False
    
    async def test_contact_extraction(self) -> bool:
        """Test contact information extraction"""
        print("🔍 Testing contact information extraction...")
        
        try:
            # Test with mock job data
            job_description = """
            Senior Python Developer needed at TechCorp India.
            Contact: HR Manager John Doe
            Email: hr@techcorp.in
            Phone: +91-98765-43210
            Location: Bangalore, India
            """
            
            company_website = "https://techcorp.in"
            
            extracted_info = await self.azure_ai.extract_contact_info_azure(
                job_description, company_website
            )
            
            if extracted_info and any(
                extracted_info.get(field) != "Not found" 
                for field in ["contact_person", "contact_email", "contact_phone"]
            ):
                print("✅ Contact extraction test successful!")
                print(f"   Extracted: {extracted_info}")
                self.test_results.append(("Contact Extraction", "PASS"))
                return True
            else:
                print("❌ Contact extraction test failed")
                self.test_results.append(("Contact Extraction", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Contact extraction test failed: {e}")
            self.test_results.append(("Contact Extraction", "FAIL"))
            return False
    
    async def test_decision_making(self) -> bool:
        """Test AI decision making"""
        print("🔍 Testing AI decision making...")
        
        try:
            # Mock job data
            from agents.base_agent import JobData
            
            job_data = JobData(
                job_title="Python Developer",
                company_name="TechCorp India",
                location="Bangalore",
                source="test"
            )
            
            user_preferences = {
                "locations": ["Bangalore", "Mumbai"],
                "skills": ["Python", "Django"],
                "experience_level": "mid"
            }
            
            decision = await self.azure_ai.make_decision_azure(job_data, user_preferences)
            
            if decision and "decision" in decision:
                print("✅ Decision making test successful!")
                print(f"   Decision: {decision}")
                self.test_results.append(("Decision Making", "PASS"))
                return True
            else:
                print("❌ Decision making test failed")
                self.test_results.append(("Decision Making", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Decision making test failed: {e}")
            self.test_results.append(("Decision Making", "FAIL"))
            return False
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("🧪 TEST RESULTS SUMMARY")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r[1] == "PASS"])
        failed_tests = total_tests - passed_tests
        
        for test_name, result in self.test_results:
            status_icon = "✅" if result == "PASS" else "❌"
            print(f"{status_icon} {test_name}: {result}")
        
        print(f"\n📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        
        if failed_tests == 0:
            print("\n🎉 All tests passed! Ready for deployment.")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please fix before deployment.")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Azure AI Integration Tests...")
        print("="*50)
        
        await self.test_azure_openai_connection()
        await self.test_web_scraping()
        await self.test_contact_extraction()
        await self.test_decision_making()
        
        self.print_test_summary()

async def main():
    """Main test function"""
    tester = AzureAITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
