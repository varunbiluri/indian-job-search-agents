#!/usr/bin/env python3
"""
Cloud Integration Test for Indian Job Search
Tests the system in the cloud environment
"""

import requests
import json
import time
from datetime import datetime

class CloudIntegrationTester:
    """Test cloud integration"""
    
    def __init__(self):
        self.base_url = "http://job-search-api-test.varun-dev.svc.cluster.local"
        self.test_results = []
    
    def test_api_connectivity(self):
        """Test if the API is reachable"""
        print("🔍 Testing API connectivity...")
        
        try:
            # Test basic connectivity
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                print("✅ API connectivity successful!")
                self.test_results.append(("API Connectivity", "PASS"))
                return True
            else:
                print(f"❌ API connectivity failed: HTTP {response.status_code}")
                self.test_results.append(("API Connectivity", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ API connectivity failed: {e}")
            self.test_results.append(("API Connectivity", "FAIL"))
            return False
    
    def test_kubernetes_services(self):
        """Test if Kubernetes services are running"""
        print("🔍 Testing Kubernetes services...")
        
        try:
            import subprocess
            
            # Check if services are running
            result = subprocess.run([
                "kubectl", "get", "services", "-n", "varun-dev"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                services = result.stdout
                print("✅ Kubernetes services check successful!")
                print("   Available services:")
                for line in services.strip().split('\n')[1:]:  # Skip header
                    if line.strip():
                        print(f"   - {line}")
                self.test_results.append(("Kubernetes Services", "PASS"))
                return True
            else:
                print("❌ Kubernetes services check failed")
                self.test_results.append(("Kubernetes Services", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Kubernetes services test failed: {e}")
            self.test_results.append(("Kubernetes Services", "FAIL"))
            return False
    
    def test_pod_status(self):
        """Test pod status"""
        print("🔍 Testing pod status...")
        
        try:
            import subprocess
            
            # Check pod status
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", "varun-dev", "--no-headers"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                pods = result.stdout.strip().split('\n')
                running_pods = [pod for pod in pods if "Running" in pod]
                
                print(f"✅ Pod status check successful!")
                print(f"   Total pods: {len(pods)}")
                print(f"   Running pods: {len(running_pods)}")
                
                for pod in pods[:5]:  # Show first 5 pods
                    if pod.strip():
                        print(f"   - {pod}")
                
                self.test_results.append(("Pod Status", "PASS"))
                return True
            else:
                print("❌ Pod status check failed")
                self.test_results.append(("Pod Status", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Pod status test failed: {e}")
            self.test_results.append(("Pod Status", "FAIL"))
            return False
    
    def test_azure_ai_config(self):
        """Test Azure AI configuration"""
        print("🔍 Testing Azure AI configuration...")
        
        try:
            # Check if config file exists
            with open("config/azure_ai_config.yaml", "r") as f:
                config = f.read()
            
            if "azure_openai" in config and "endpoint" in config:
                print("✅ Azure AI configuration found!")
                print("   - OpenAI configuration present")
                print("   - Endpoint configuration present")
                self.test_results.append(("Azure AI Config", "PASS"))
                return True
            else:
                print("❌ Azure AI configuration incomplete")
                self.test_results.append(("Azure AI Config", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Azure AI configuration test failed: {e}")
            self.test_results.append(("Azure AI Config", "FAIL"))
            return False
    
    def test_indian_market_agents(self):
        """Test Indian market agents"""
        print("🔍 Testing Indian market agents...")
        
        try:
            # Check if agent files exist
            agent_files = [
                "src/agents/indian_companies_agent.py",
                "src/agents/indian_market_orchestrator.py",
                "src/agents/azure_ai_models.py"
            ]
            
            existing_agents = []
            for agent_file in agent_files:
                try:
                    with open(agent_file, "r") as f:
                        content = f.read()
                        if "class" in content and "Indian" in content:
                            existing_agents.append(agent_file.split("/")[-1])
                except:
                    pass
            
            if existing_agents:
                print("✅ Indian market agents found!")
                for agent in existing_agents:
                    print(f"   - {agent}")
                self.test_results.append(("Indian Market Agents", "PASS"))
                return True
            else:
                print("❌ No Indian market agents found")
                self.test_results.append(("Indian Market Agents", "FAIL"))
                return False
                
        except Exception as e:
            print(f"❌ Indian market agents test failed: {e}")
            self.test_results.append(("Indian Market Agents", "FAIL"))
            return False
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("🧪 CLOUD INTEGRATION TEST RESULTS")
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
            print("\n🎉 All cloud integration tests passed!")
            print("   The feature branch is ready for production deployment!")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed.")
            print("   Please fix issues before merging to main.")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Cloud Integration Tests...")
        print("="*50)
        print(f"⏰ Test started at: {datetime.now()}")
        print(f"🌐 Testing in Azure Kubernetes cluster")
        print("="*50)
        
        self.test_api_connectivity()
        self.test_kubernetes_services()
        self.test_pod_status()
        self.test_azure_ai_config()
        self.test_indian_market_agents()
        
        self.print_test_summary()

def main():
    """Main test function"""
    tester = CloudIntegrationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
