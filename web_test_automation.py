"""
Web Test Automation Tool with Ollama Vision Integration

This script creates a test automation system that:
1. Navigates to a web application
2. Handles login with provided credentials
3. Navigates through reports
4. Analyzes data on each page using vision-based AI
"""

import os
import time
import json
import argparse
import requests
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from PIL import Image
import io
import base64

def check_ollama_server():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def verify_dependencies():
    """Verify all required dependencies are available"""
    missing_deps = []
    
    # Check Chrome and ChromeDriver
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
    except Exception as e:
        missing_deps.append(f"Chrome/ChromeDriver error: {str(e)}")
    
    # Check Ollama server
    if not check_ollama_server():
        missing_deps.append("Ollama server is not running. Please start it with 'ollama serve'")
    
    return missing_deps

class WebTestAutomation:
    def __init__(self, url, username, password, ollama_model="llava:latest", headless=False):
        """
        Initialize the test automation tool
        
        Args:
            url (str): The URL of the web application to test
            username (str): Login username
            password (str): Login password
            ollama_model (str): The Ollama vision model to use
            headless (bool): Run browser in headless mode
        """
        self.url = url
        self.username = username
        self.password = password
        self.ollama_model = ollama_model
        
        # Set up webdriver options
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        
        # Initialize webdriver with automatic ChromeDriver management
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
        # Results storage
        self.test_results = []
    
    def capture_screenshot(self):
        """Capture a screenshot of the current page"""
        screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(io.BytesIO(screenshot))
        return image
    
    def analyze_with_ollama(self, image, prompt):
        """
        Analyze a screenshot using Ollama's vision capabilities
        
        Args:
            image: PIL Image object
            prompt (str): The prompt to send to Ollama
            
        Returns:
            str: Ollama's response
        """
        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Prepare API request to Ollama
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "images": [img_base64],
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No response")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    def navigate_to_site(self):
        """Navigate to the target website"""
        print(f"Navigating to {self.url}")
        self.driver.get(self.url)
        time.sleep(2)  # Wait for page to load
        
        # Analyze the landing page
        image = self.capture_screenshot()
        analysis = self.analyze_with_ollama(
            image, 
            "This is a login page. Identify the username and password input fields and the login button."
        )
        print("Page analysis:", analysis)
        return analysis
    
    def login(self):
        """Perform login with credentials"""
        try:
            print("Attempting login...")
            start_time = time.time()
            
            # Capture initial state for analysis
            image = self.capture_screenshot()
            analysis = self.analyze_with_ollama(
                image,
                "Focus only on login form elements. Locate username field, password field, and login/signin button."
            )
            print("Login form analysis:", analysis)
            
            # Try to find login elements based on common attributes
            try:
                username_field = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='text'], input[type='email'], input[id*='user'], input[name*='user'], input[id*='email'], input[name*='email']")
                ))
            except TimeoutException:
                print("Username field not found with standard selectors, trying alternative methods...")
                # Try to find by placeholder text
                username_field = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[placeholder*='user' i], input[placeholder*='email' i], input[aria-label*='user' i], input[aria-label*='email' i]")
                ))
            
            try:
                password_field = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']")
                ))
            except TimeoutException:
                print("Password field not found with standard selector, trying alternative methods...")
                password_field = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[placeholder*='password' i], input[aria-label*='password' i]")
                ))
            
            # Enter credentials with clear first
            username_field.clear()
            username_field.send_keys(self.username)
            time.sleep(0.5)  # Small delay between fields
            
            password_field.clear()
            password_field.send_keys(self.password)
            time.sleep(0.5)  # Small delay before clicking login
            
            # Find login button with expanded selectors
            login_button = None
            button_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button[id*='login' i]",
                "button[class*='login' i]",
                "button[id*='signin' i]",
                "button[class*='signin' i]",
                "a[href*='login' i]",
                "a[href*='signin' i]",
                "button:contains('Sign in')",
                "button:contains('Login')"
            ]
            
            for selector in button_selectors:
                try:
                    login_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    break
                except:
                    continue
            
            if not login_button:
                raise Exception("Login button not found")
            
            # Click login
            login_button.click()
            
            # Wait for login to complete with increased timeout
            time.sleep(3)
            
            # Verify login success
            image = self.capture_screenshot()
            login_verification = self.analyze_with_ollama(
                image,
                "Has the login been successful? Look for: 1) Dashboard elements 2) Navigation menu 3) User profile 4) Logged-in state indicators"
            )
            
            duration = time.time() - start_time
            
            if "dashboard" in login_verification.lower() or "success" in login_verification.lower():
                print("Login successful!")
                self.test_results.append({
                    "step": "login",
                    "status": "success",
                    "details": login_verification,
                    "duration": round(duration, 2)
                })
                return True
            else:
                print("Login may have failed. AI analysis:", login_verification)
                self.test_results.append({
                    "step": "login",
                    "status": "uncertain",
                    "details": login_verification,
                    "duration": round(duration, 2)
                })
                return False
                
        except TimeoutException as e:
            print(f"Timeout during login - elements not found: {str(e)}")
            self.test_results.append({
                "step": "login",
                "status": "error",
                "details": f"Timeout - login elements not found: {str(e)}",
                "duration": time.time() - start_time
            })
            return False
        except Exception as e:
            print(f"Error during login: {str(e)}")
            self.test_results.append({
                "step": "login",
                "status": "error",
                "details": f"Login failed: {str(e)}",
                "duration": time.time() - start_time
            })
            return False
    
    def find_navigation_elements(self):
        """Identify navigation elements on the page"""
        try:
            image = self.capture_screenshot()
            nav_analysis = self.analyze_with_ollama(
                image,
                "Identify all navigation links or menu items that lead to different reports or pages."
            )
            
            print("Navigation analysis:", nav_analysis)
            
            # Try to find navigation elements
            nav_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "nav a, .sidebar a, .navigation a, .menu a, ul.nav a, .navbar a, a[href]:not([href='#']):not([href^='javascript'])"
            )
            
            # Extract info about each nav element
            nav_info = []
            for idx, elem in enumerate(nav_elements):
                try:
                    text = elem.text.strip()
                    href = elem.get_attribute("href")
                    if text and href:
                        nav_info.append({
                            "index": idx,
                            "text": text,
                            "href": href
                        })
                except:
                    continue
            
            print(f"Found {len(nav_info)} potential navigation elements")
            self.test_results.append({
                "step": "navigation_discovery", 
                "status": "success", 
                "details": nav_analysis,
                "nav_elements": nav_info
            })
            
            return nav_info
        
        except Exception as e:
            print(f"Error finding navigation elements: {e}")
            self.test_results.append({
                "step": "navigation_discovery", 
                "status": "error", 
                "details": str(e)
            })
            return []
    
    def navigate_and_test_reports(self):
        """Navigate through reports and test each page"""
        nav_elements = self.find_navigation_elements()
        
        for idx, nav in enumerate(nav_elements):
            print(f"Testing navigation element {idx+1}/{len(nav_elements)}: {nav['text']}")
            
            # Store current URL to go back later
            current_url = self.driver.current_url
            
            try:
                # Click the navigation element
                nav_element = self.driver.find_elements(By.CSS_SELECTOR, 
                    "nav a, .sidebar a, .navigation a, .menu a, ul.nav a, .navbar a, a[href]:not([href='#']):not([href^='javascript'])"
                )[nav['index']]
                
                nav_element.click()
                time.sleep(3)  # Wait for page load
                
                # Check if URL changed
                if self.driver.current_url == current_url:
                    print(f"Navigation to {nav['text']} didn't change URL - might be a dynamic page component")
                
                # Analyze the report page
                image = self.capture_screenshot()
                report_analysis = self.analyze_with_ollama(
                    image,
                    "This is a report page. Analyze what type of report this is, what data is being shown, and if the data appears to be loaded correctly or if there are any errors."
                )
                
                print(f"Report analysis for {nav['text']}:", report_analysis)
                
                # Look for data elements
                data_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "table, .chart, .graph, .data-table, [data-role='grid'], .grid, .report-data, .report-container"
                )
                
                data_loaded = len(data_elements) > 0
                
                self.test_results.append({
                    "step": f"report_{nav['text']}",
                    "status": "success" if data_loaded else "warning",
                    "url": self.driver.current_url,
                    "data_elements_found": len(data_elements),
                    "ai_analysis": report_analysis
                })
                
                # Navigate back to main page
                self.driver.get(current_url)
                time.sleep(2)  # Wait for page to load
                
            except Exception as e:
                print(f"Error testing report {nav['text']}: {e}")
                self.test_results.append({
                    "step": f"report_{nav['text']}",
                    "status": "error",
                    "details": str(e)
                })
                
                # Try to get back to main page
                self.driver.get(current_url)
                time.sleep(2)
    
    def generate_html_report(self):
        """Generate an HTML report of the test results"""
        import json
        from datetime import datetime
        import os

        try:
            # Get absolute paths
            script_dir = os.path.dirname(os.path.abspath(__file__))
            reports_dir = os.path.join(script_dir, "test_reports")
            
            # Create reports directory
            os.makedirs(reports_dir, exist_ok=True)
            print(f"\nReports directory: {reports_dir}")

            # Generate report filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"test_report_{timestamp}.html")
            
            # Get site title properly
            site_title = "Unknown"
            if hasattr(self, 'driver'):
                try:
                    site_title = self.driver.title
                    # If site title is empty or matches username, use URL domain instead
                    if not site_title or site_title == self.username:
                        from urllib.parse import urlparse
                        parsed_url = urlparse(self.url)
                        site_title = parsed_url.netloc
                except:
                    site_title = "Error retrieving title"
            
            # Prepare results data
            results = {
                "siteUrl": self.url,
                "siteTitle": site_title,
                "username": self.username,
                "visionModel": self.ollama_model,
                "visionMode": getattr(self, 'vision_system', 'hybrid'),
                "totalTests": len(self.test_results),
                "passedTests": sum(1 for result in self.test_results if result.get('status') == 'success'),
                "failedTests": sum(1 for result in self.test_results if result.get('status') == 'error'),
                "duration": f"{getattr(self, 'total_duration', 0)}s",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "steps": []
            }

            # Convert test results to step format
            for result in self.test_results:
                step = {
                    "name": result.get('step', 'Unknown Step'),
                    "status": result.get('status', 'UNKNOWN').upper(),
                    "details": result.get('details', 'No details available'),
                    "time": f"{result.get('duration', 0)}s"
                }
                results['steps'].append(step)

            # Read template
            template_path = os.path.join(script_dir, "test_results_template.html")
            print(f"Template path: {template_path}")
            
            with open(template_path, "r", encoding='utf-8') as f:
                template = f.read()
            
            # Generate test results HTML rows
            test_results_html = ""
            for step in results['steps']:
                test_results_html += f"""
                <tr>
                    <td>{step['name']}</td>
                    <td><span class="status status-{step['status'].lower()}">{step['status']}</span></td>
                    <td class="details-cell">{step['details']}</td>
                    <td>{step['time']}</td>
                </tr>
                """
            
            # Replace placeholders in template
            report_content = template
            report_content = report_content.replace("{{TIMESTAMP}}", results['timestamp'])
            report_content = report_content.replace("{{SITE_URL}}", results['siteUrl'])
            report_content = report_content.replace("{{SITE_TITLE}}", results['siteTitle'])
            report_content = report_content.replace("{{USERNAME}}", results['username'])
            report_content = report_content.replace("{{VISION_MODEL}}", results['visionModel'])
            report_content = report_content.replace("{{VISION_MODE}}", results['visionMode'])
            report_content = report_content.replace("{{TOTAL_TESTS}}", str(results['totalTests']))
            report_content = report_content.replace("{{PASSED_TESTS}}", str(results['passedTests']))
            report_content = report_content.replace("{{FAILED_TESTS}}", str(results['failedTests']))
            report_content = report_content.replace("{{DURATION}}", results['duration'])
            report_content = report_content.replace("{{TEST_RESULTS}}", test_results_html)

            # Save report
            with open(report_file, "w", encoding='utf-8') as f:
                f.write(report_content)

            print(f"Test report generated: {report_file}")
            return report_file

        except Exception as e:
            print(f"\nError generating report: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_full_test(self):
        """Run the complete test sequence and generate report"""
        start_time = time.time()
        
        try:
            # Existing test steps
            self.navigate_to_site()
            self.login()
            nav_elements = self.find_navigation_elements()
            self.navigate_and_test_reports()
            
        except Exception as e:
            self.test_results.append({
                "step": "test_execution",
                "status": "error",
                "details": f"Test execution failed: {str(e)}",
                "duration": time.time() - start_time
            })
        finally:
            # Calculate total duration
            self.total_duration = round(time.time() - start_time, 2)
            
            # Generate HTML report
            report_file = self.generate_html_report()
            
            # Clean up
            if hasattr(self, 'driver'):
                self.driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Test Automation Tool")
    parser.add_argument("--url", required=True, help="URL of the application to test")
    parser.add_argument("--username", required=True, help="Login username")
    parser.add_argument("--password", required=True, help="Login password")
    parser.add_argument("--model", default="llava:latest", help="Ollama vision model to use")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    # Verify dependencies before starting
    print("Verifying dependencies...")
    missing_deps = verify_dependencies()
    if missing_deps:
        print("\nError: Missing or incorrect dependencies:")
        for dep in missing_deps:
            print(f"- {dep}")
        print("\nPlease fix these issues and try again.")
        sys.exit(1)
    
    print("All dependencies verified successfully!")
    print(f"Starting test for URL: {args.url}")
    
    try:
        # Run the test
        tester = WebTestAutomation(
            url=args.url,
            username=args.username,
            password=args.password,
            ollama_model=args.model,
            headless=args.headless
        )
        
        test_results = tester.run_full_test()
        print("Test complete!")
        
    except Exception as e:
        print(f"\nError during test execution: {str(e)}")
        sys.exit(1)