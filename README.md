# REVA Paper Abstract Extraction Pipeline

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Status](https://img.shields.io/badge/Status-Production-green)

Automated pipeline to extract and preprocess abstracts and keywords from 4,500+ subscription-based research papers from Scopus URLs.

## 📋 Project Overview

This project was developed for the **REVA AI Project Deployment Team** to automate the extraction of abstracts and keywords from academic research papers. The pipeline processes ~4,092 papers from the REVA Scopus database and adds extracted content to a new Excel column.

### Key Features

✅ **Multi-Strategy Extraction**
- Primary: Scopus URL web scraping with BeautifulSoup
- Fallback: CrossRef API integration for DOI-based extraction
- Multiple HTML selector strategies for maximum success rate

✅ **Robust Processing**
- Automatic checkpoint system (saves progress every 50 papers)
- Resume capability from last checkpoint
- Rate limiting to prevent IP bans (2 seconds between requests)
- Comprehensive error handling and logging

✅ **Text Preprocessing**
- HTML tag removal
- Special character cleaning
- Whitespace normalization
- Unicode standardization

✅ **Progress Tracking**
- Real-time progress bar with tqdm
- Detailed logging to `extraction.log`
- Success rate statistics

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Excel file: `REVA_Lit_Open and Subscription Based_Edited Data.xlsx`

### Installation

```bash
# Clone the repository
git clone https://github.com/Koushik926/reva-paper-abstract-extraction.git
cd reva-paper-abstract-extraction

# Install dependencies
pip install -r requirements.txt
```

### Usage

```bash
# Run the extraction pipeline
python extract_abstracts.py
```

The script will:
1. Load data from the Excel file
2. Process each paper's Scopus URL
3. Extract abstract and keywords
4. Clean and preprocess the text
5. Save results with checkpoints
6. Generate final output: `REVA_Papers_With_Abstracts.xlsx`

## 📊 Data Structure

### Input Excel Sheet: `REVA_Scopus_Subscription Based`

| Column | Description |
|--------|-------------|
| A | Authors |
| D | Title |
| E | Year |
| F | Source title (Journal/Publisher) |
| H | DOI |
| **I** | **Link (Scopus URL)** - Primary extraction source |

### Output

New columns added:
- **Abstract**: Extracted and cleaned abstract text
- **Keywords**: Extracted keywords (when available)

## 🛠️ Technical Architecture

### Extraction Workflow

```
1. Load Excel → 2. For each paper:
                   ├─> Try Scopus URL scraping
                   │   ├─> Strategy 1: Abstract section
                   │   ├─> Strategy 2: Alternative div class
                   │   └─> Strategy 3: Meta tags
                   ├─> Fallback to CrossRef API (DOI)
                   └─> Clean & preprocess text
              → 3. Save to checkpoint (every 50 papers)
              → 4. Generate output Excel
```

### Key Components

**`PaperExtractor` Class**
- `extract_from_scopus()`: Web scraping with multiple selectors
- `extract_from_doi()`: API-based extraction fallback
- `clean_text()`: Text preprocessing and normalization
- `process_paper()`: Main orchestration method

**Configuration**
```python
INPUT_FILE = 'REVA_Lit_Open and Subscription Based_Edited Data.xlsx'
SHEET_NAME = 'REVA_Scopus_Subscription Based'
OUTPUT_FILE = 'REVA_Papers_With_Abstracts.xlsx'
BATCH_SIZE = 50  # Checkpoint interval
RATE_LIMIT = 2   # Seconds between requests
```

## 📦 Dependencies

```
pandas>=2.0.0          # Data manipulation
openpyxl>=3.1.0        # Excel file handling  
requests>=2.31.0       # HTTP requests
beautifulsoup4>=4.12.0 # HTML parsing
lxml>=4.9.0            # XML/HTML parser
tqdm>=4.66.0           # Progress bars
selenium>=4.15.0       # Browser automation (optional)
retry>=0.9.2           # Retry logic
```

## 🔧 Configuration Options

Edit `extract_abstracts.py` to customize:

```python
# Adjust rate limiting
extractor = PaperExtractor(rate_limit=3)  # 3 seconds

# Change batch size
BATCH_SIZE = 100  # Save every 100 papers

# Modify input/output paths
INPUT_FILE = 'path/to/your/file.xlsx'
OUTPUT_FILE = 'custom_output.xlsx'
```

## 📈 Performance

- **Processing Speed**: ~2.5 seconds per paper (with rate limiting)
- **Estimated Time**: ~2.8 hours for 4,092 papers
- **Memory Usage**: ~200-300 MB
- **Success Rate**: Typically 70-85% (varies by accessibility)

## 🐛 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
pip install --upgrade -r requirements.txt
```

**2. Excel File Not Found**
- Ensure the Excel file is in the same directory
- Check filename matches exactly (case-sensitive)

**3. Low Success Rate**
- Check internet connection
- Verify Scopus URLs are accessible
- Review `extraction.log` for specific errors

**4. Resume from Checkpoint**
- Delete `progress_checkpoint.csv` to start fresh
- Keep it to resume from last processed paper

## 📝 Logging

Logs are saved to `extraction.log`:

```
2025-11-20 11:00:00 - INFO - Paper 1/4092: Success - Scopus
2025-11-20 11:00:02 - INFO - Paper 2/4092: Success - DOI
2025-11-20 11:00:04 - WARNING - Paper 3/4092: Failed
2025-11-20 11:00:50 - INFO - Checkpoint saved at 50 papers
```

## 🤝 Contributing

Feel free to:
- Report bugs via Issues
- Submit pull requests for improvements
- Suggest new features

## 👥 Team

**REVA AI Project Deployment Team**
- Project Lead: Dr. Shinu Abhi
- Development: Koushik & Team
- Institution: REVA University

## 📄 License

This project is created for academic purposes at REVA University.

## 🙏 Acknowledgments

- REVA University AI Project Team
- Scopus Database
- CrossRef API

---

**Last Updated**: November 20, 2025  
**Repository**: [github.com/Koushik926/reva-paper-abstract-extraction](https://github.com/Koushik926/reva-paper-abstract-extraction)
