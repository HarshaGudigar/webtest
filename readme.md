# Web Test Automation Tool with AI Vision

A powerful web testing automation tool that combines Selenium WebDriver with Ollama's vision capabilities for intelligent web application testing.

## Features

- 🤖 Automated web navigation and testing
- 🔐 Automated login handling
- 👁️ AI-powered visual analysis using Ollama
- 📊 Comprehensive report generation
- 🔄 Smart element detection and navigation
- 🚀 Multiple vision system modes (hybrid, heuristic, full vision)

## Prerequisites

Before running the tool, ensure you have the following installed:

### Required Software

- Python 3.7 or higher
- Chrome browser
- ChromeDriver (matching your Chrome version)
- Ollama (for vision capabilities)

### Python Dependencies

```bash
pip install selenium requests pillow webdriver_manager
```

## Installation

1. **Create and activate a virtual environment (recommended)**

   Windows:
   ```bash
   python -m venv webtest_env
   webtest_env\Scripts\activate
   ```

   macOS/Linux:
   ```bash
   python -m venv webtest_env
   source webtest_env/bin/activate
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Ollama Server**
   ```bash
   ollama serve
   ```
   Note: If you see an error about port 11434 being in use, Ollama is already running.

4. **Pull Required Vision Model**
   ```bash
   ollama pull llava     # Full model
   # OR
   ollama pull bakllava  # Smaller model (recommended)
   ```

## Usage

### Command Line Options

- `--url`: Target website URL (required)
- `--username`: Login username (required)
- `--password`: Login password (required)
- `--model`: Ollama vision model (default: "llava:latest")
- `--headless`: Run in headless mode (optional)
- `--vision-system`: Vision system mode (optional, default: hybrid)

### Example Commands

**Basic Test Run**
```bash
python web_test_automation.py --url "https://your-app-url.com" --username "testuser" --password "testpass"
```

**Real Example (Ollama Website)**
```bash
python web_test_automation.py --url "https://ollama.com/signin" --username "testuser" --password "testpass" --model "llava:latest"
```

**Headless Mode**
```bash
python web_test_automation.py --url "https://ollama.com/signin" --username "testuser" --password "testpass" --headless
```

## Test Reports

### Report Locations

The tool generates HTML test reports in the following locations:
- Reports Directory: `./test_reports/`
- Report Files: `test_report_YYYYMMDD_HHMMSS.html`
- Template File: `test_results_template.html`

### Report Contents

Each HTML report includes:
- Test Configuration Details
- Site Information
- Login Status
- Navigation Results
- Vision Analysis Results
- Test Duration and Metrics
- Step-by-Step Results

### Viewing Reports

1. Reports are automatically generated after each test run
2. Open the generated HTML file in any web browser
3. Reports are time-stamped for easy tracking
4. Latest report path is displayed at the end of each test run

## Vision System Modes

1. **Hybrid Mode (Default)**
   - Combines traditional automation with AI vision
   - Uses heuristics when possible for better performance
   - Falls back to vision model when needed

2. **Heuristic Mode**
   - Uses only traditional automation methods
   - Faster execution
   - No vision model dependency

3. **Full Vision Mode**
   - Relies primarily on AI vision analysis
   - Most comprehensive but slower
   - Best for complex or dynamic UIs

## Troubleshooting

- Ensure ChromeDriver version matches your Chrome browser version
- Verify Ollama is running (`ollama serve`)
- Check network connectivity for API calls
- Ensure proper permissions for browser automation
- Check test reports for detailed error information
- GPU errors during testing are usually non-critical

## Contributing

Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.