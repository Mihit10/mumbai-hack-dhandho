import requests
import os
from typing import Optional
from bs4 import BeautifulSoup
import time

class PDFFetcherAgent:
    """
    Fetches quarterly result PDFs from company websites/exchanges
    """
    
    def __init__(self):
        self.download_dir = "data/pdfs"
        os.makedirs(self.download_dir, exist_ok=True)
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Company website patterns (for major companies)
        self.company_ir_urls = {
            "TCS": "https://www.tcs.com/investor-relations",
            "INFY": "https://www.infosys.com/investors/reports-filings.html",
            "RELIANCE": "https://www.ril.com/InvestorRelations/FinancialReporting.aspx",
            "WIPRO": "https://www.wipro.com/investors/quarterly-results/",
            # Add more as needed
        }
    
    async def fetch_result_pdf(self, symbol: str) -> Optional[str]:
        """
        Fetch the latest quarterly result PDF for a company
        """
        print(f"🔍 Searching for {symbol} results PDF...")
        
        # Strategy 1: Try company IR website
        pdf_path = await self._fetch_from_company_site(symbol)
        if pdf_path:
            return pdf_path
        
        # Strategy 2: Try BSE/NSE announcements
        pdf_path = await self._fetch_from_exchange(symbol)
        if pdf_path:
            return pdf_path
        
        # Strategy 3: Generate mock PDF for demo (with real-looking data)
        print(f"⚠️ Could not find real PDF, using demo data for {symbol}")
        return await self._create_demo_pdf(symbol)
    
    async def _fetch_from_company_site(self, symbol: str) -> Optional[str]:
        """
        Try to fetch from company's investor relations page
        """
        if symbol not in self.company_ir_urls:
            return None
        
        try:
            url = self.company_ir_urls[symbol]
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for PDF links containing keywords
            keywords = ['result', 'quarterly', 'financial', 'Q4', 'Q3', 'Q2', 'Q1']
            pdf_links = soup.find_all('a', href=True)
            
            for link in pdf_links:
                href = link['href']
                text = link.get_text().lower()
                
                if '.pdf' in href and any(kw in text for kw in keywords):
                    pdf_url = href if href.startswith('http') else url + href
                    return await self._download_pdf(pdf_url, symbol)
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching from company site: {e}")
            return None
    
    async def _fetch_from_exchange(self, symbol: str) -> Optional[str]:
        """
        Try to fetch from BSE/NSE announcements
        """
        # BSE announcements API (simplified)
        try:
            bse_url = f"https://www.bseindia.com/stockinfo/AnnoucementDetail.aspx?symbol={symbol}"
            # This would require more complex scraping with JavaScript handling
            # Skipping for now as it needs Selenium/Playwright
            return None
        except:
            return None
    
    async def _download_pdf(self, url: str, symbol: str) -> Optional[str]:
        """
        Download PDF from URL
        """
        try:
            print(f"📥 Downloading PDF from {url}")
            response = requests.get(url, headers=self.headers, timeout=30, stream=True)
            
            if response.status_code == 200:
                filename = f"{symbol}_{int(time.time())}.pdf"
                filepath = os.path.join(self.download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ Downloaded: {filepath}")
                return filepath
            
            return None
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return None
    
    async def _create_demo_pdf(self, symbol: str) -> Optional[str]:
        """
        For hackathon demo: Create a mock PDF path that the parser can handle
        We'll return a marker that tells the parser to use demo data
        """
        # Return a special marker that the parser will recognize
        return f"DEMO:{symbol}"