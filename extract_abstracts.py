"""
REVA Paper Abstract Extraction Pipeline
Extracts abstracts and keywords from 4.5k subscription-based research papers from Scopus URLs
Author: REVA AI Project Team
Date: November 2025
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from urllib.parse import urlparse
import json
from typing import Dict, Optional, Tuple
import os
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extraction.log'),
        logging.StreamHandler()
    ]
)

class PaperExtractor:
    """Main class for extracting abstracts and keywords from research papers"""
    
    def __init__(self, rate_limit=2):
        self.rate_limit = rate_limit  # seconds between requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,;:()\-]', '', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def extract_from_scopus(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract abstract and keywords from Scopus URL"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Strategy 1: Look for abstract section
            abstract = None
            abstract_section = soup.find('section', {'id': 'abstractSection'})
            if abstract_section:
                abstract_text = abstract_section.find('div', class_='abstract')
                if abstract_text:
                    abstract = self.clean_text(abstract_text.get_text())
            
            # Strategy 2: Try alternative selectors
            if not abstract:
                abstract_div = soup.find('div', {'class': 'abstract'})
                if abstract_div:
                    abstract = self.clean_text(abstract_div.get_text())
            
            # Strategy 3: Look for meta tags
            if not abstract:
                meta_abstract = soup.find('meta', {'name': 'description'})
                if meta_abstract:
                    abstract = self.clean_text(meta_abstract.get('content', ''))
            
            # Extract keywords
            keywords = None
            keywords_section = soup.find('span', {'class': 'keyword'})
            if keywords_section:
                keywords = self.clean_text(keywords_section.get_text())
            
            return abstract, keywords
            
        except Exception as e:
            logging.error(f"Error extracting from Scopus URL {url}: {str(e)}")
            return None, None
    
    def extract_from_doi(self, doi: str) -> Tuple[Optional[str], Optional[str]]:
        """Fallback: Extract using DOI via CrossRef API"""
        try:
            api_url = f"https://api.crossref.org/works/{doi}"
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            abstract = data.get('message', {}).get('abstract', '')
            
            if abstract:
                return self.clean_text(abstract), None
            
        except Exception as e:
            logging.debug(f"CrossRef API failed for DOI {doi}: {str(e)}")
        
        return None, None
    
    def process_paper(self, row: pd.Series) -> Dict[str, str]:
        """Process a single paper and extract abstract"""
        scopus_url = row.get('Link', '')
        doi = row.get('DOI', '')
        
        result = {
            'Abstract': '',
            'Keywords': '',
            'Status': 'Failed'
        }
        
        # Try Scopus URL first
        if scopus_url:
            abstract, keywords = self.extract_from_scopus(scopus_url)
            if abstract:
                result['Abstract'] = abstract
                result['Keywords'] = keywords or ''
                result['Status'] = 'Success - Scopus'
                return result
        
        # Fallback to DOI
        if doi:
            abstract, keywords = self.extract_from_doi(doi)
            if abstract:
                result['Abstract'] = abstract
                result['Keywords'] = keywords or ''
                result['Status'] = 'Success - DOI'
                return result
        
        return result

def main():
    """Main execution function"""
    
    # Configuration
    INPUT_FILE = 'REVA_Lit_Open and Subscription Based_Edited Data.xlsx'
    SHEET_NAME = 'REVA_Scopus_Subscription Based'
    OUTPUT_FILE = 'REVA_Papers_With_Abstracts.xlsx'
    CHECKPOINT_FILE = 'progress_checkpoint.csv'
    BATCH_SIZE = 50
    
    print("="*60)
    print("REVA Paper Abstract Extraction Pipeline")
    print("="*60)
    
    # Load data
    print(f"\nLoading data from {INPUT_FILE}...")
    df = pd.read_excel(INPUT_FILE, sheet_name=SHEET_NAME)
    print(f"Loaded {len(df)} papers")
    
    # Check if checkpoint exists
    start_index = 0
    if os.path.exists(CHECKPOINT_FILE):
        checkpoint_df = pd.read_csv(CHECKPOINT_FILE)
        df_merged = df.merge(checkpoint_df, on='Link', how='left')
        df['Abstract'] = df_merged['Abstract']
        df['Keywords'] = df_merged['Keywords']
        start_index = df['Abstract'].notna().sum()
        print(f"\nResuming from checkpoint: {start_index} papers already processed")
    else:
        df['Abstract'] = ''
        df['Keywords'] = ''
    
    # Initialize extractor
    extractor = PaperExtractor(rate_limit=2)
    
    # Process papers
    print(f"\nProcessing papers {start_index} to {len(df)}...")
    
    for i in tqdm(range(start_index, len(df)), desc="Extracting abstracts"):
        try:
            result = extractor.process_paper(df.iloc[i])
            
            df.at[i, 'Abstract'] = result['Abstract']
            df.at[i, 'Keywords'] = result['Keywords']
            
            # Log progress
            if result['Status'].startswith('Success'):
                logging.info(f"Paper {i+1}/{len(df)}: {result['Status']}")
            else:
                logging.warning(f"Paper {i+1}/{len(df)}: Failed")
            
            # Save checkpoint every BATCH_SIZE papers
            if (i + 1) % BATCH_SIZE == 0:
                checkpoint_cols = ['Link', 'Abstract', 'Keywords']
                df[checkpoint_cols].to_csv(CHECKPOINT_FILE, index=False)
                logging.info(f"Checkpoint saved at {i+1} papers")
            
            # Rate limiting
            time.sleep(extractor.rate_limit)
            
        except Exception as e:
            logging.error(f"Error processing paper {i+1}: {str(e)}")
            continue
    
    # Save final output
    print(f"\nSaving results to {OUTPUT_FILE}...")
    df.to_excel(OUTPUT_FILE, index=False)
    
    # Statistics
    success_count = df['Abstract'].astype(bool).sum()
    success_rate = (success_count / len(df)) * 100
    
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)
    print(f"Total papers: {len(df)}")
    print(f"Successfully extracted: {success_count}")
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Output saved to: {OUTPUT_FILE}")
    print("="*60)
    
    # Cleanup checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

if __name__ == '__main__':
    main()
