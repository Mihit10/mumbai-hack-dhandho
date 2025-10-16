import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
from typing import List, Dict

class DateScraperAgent:
    """
    Scrapes upcoming quarterly result dates from NSE/BSE
    """
    
    def __init__(self):
        self.nse_url = "https://www.nseindia.com/api/corporates-corporateActions"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Popular companies for demo
        self.demo_companies = [
            {"symbol": "TCS", "name": "Tata Consultancy Services"},
            {"symbol": "INFY", "name": "Infosys"},
            {"symbol": "RELIANCE", "name": "Reliance Industries"},
            {"symbol": "HDFCBANK", "name": "HDFC Bank"},
            {"symbol": "ICICIBANK", "name": "ICICI Bank"},
            {"symbol": "WIPRO", "name": "Wipro"},
            {"symbol": "SBIN", "name": "State Bank of India"},
            {"symbol": "BHARTIARTL", "name": "Bharti Airtel"},
            {"symbol": "ITC", "name": "ITC Limited"},
            {"symbol": "KOTAKBANK", "name": "Kotak Mahindra Bank"},
            {"symbol": "LT", "name": "Larsen & Toubro"},
            {"symbol": "AXISBANK", "name": "Axis Bank"},
            {"symbol": "ASIANPAINT", "name": "Asian Paints"},
            {"symbol": "MARUTI", "name": "Maruti Suzuki"},
            {"symbol": "TITAN", "name": "Titan Company"},
            {"symbol": "HINDUNILVR", "name": "Hindustan Unilever"},
            {"symbol": "BAJFINANCE", "name": "Bajaj Finance"},
            {"symbol": "TECHM", "name": "Tech Mahindra"},
            {"symbol": "SUNPHARMA", "name": "Sun Pharma"},
            {"symbol": "ULTRACEMCO", "name": "UltraTech Cement"},
        ]
    
    async def fetch_result_dates(self, limit: int = 20) -> List[Dict]:
        """
        Fetch upcoming result dates
        For hackathon: Mix of real scraping + generated data for demo
        """
        try:
            # Try real NSE API first (may require session cookies)
            real_data = await self._fetch_from_nse()
            if real_data:
                return real_data[:limit]
        except Exception as e:
            print(f"⚠️ NSE scraping failed (expected): {e}")
        
        # Fallback: Generate realistic demo data
        print("📊 Generating demo result dates...")
        return self._generate_demo_dates(limit)
    
    async def _fetch_from_nse(self) -> List[Dict]:
        """
        Attempt to fetch real data from NSE
        Note: NSE blocks simple requests, needs session handling
        """
        session = requests.Session()
        
        # First, get cookies by visiting homepage
        session.get("https://www.nseindia.com", headers=self.headers, timeout=5)
        
        # Then fetch corporate actions
        response = session.get(
            self.nse_url,
            headers=self.headers,
            params={"index": "equities"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            for item in data:
                if "result" in item.get("subject", "").lower():
                    results.append({
                        "company_symbol": item.get("symbol"),
                        "company_name": item.get("company"),
                        "result_date": item.get("exDate"),
                        "quarter": self._determine_quarter(item.get("exDate")),
                        "financial_year": self._determine_fy(item.get("exDate"))
                    })
            
            return results
        
        return []
    
    def _generate_demo_dates(self, limit: int) -> List[Dict]:
        """
        Generate realistic upcoming result dates for demo
        """
        results = []
        base_date = datetime.now()
        
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        current_quarter = (base_date.month - 1) // 3
        
        for i, company in enumerate(self.demo_companies[:limit]):
            # Spread dates over next 30 days
            days_ahead = random.randint(1, 30)
            result_date = base_date + timedelta(days=days_ahead)
            
            # Rotate quarters
            quarter = quarters[(current_quarter + (i % 4)) % 4]
            
            results.append({
                "company_symbol": company["symbol"],
                "company_name": company["name"],
                "result_date": result_date.strftime("%Y-%m-%d"),
                "quarter": quarter,
                "financial_year": f"FY{result_date.year % 100}"
            })
        
        # Sort by date
        results.sort(key=lambda x: x["result_date"])
        
        return results
    
    def _determine_quarter(self, date_str: str) -> str:
        """Determine quarter from date"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            month = date.month
            if month in [4, 5, 6]:
                return "Q1"
            elif month in [7, 8, 9]:
                return "Q2"
            elif month in [10, 11, 12]:
                return "Q3"
            else:
                return "Q4"
        except:
            return "Q4"
    
    def _determine_fy(self, date_str: str) -> str:
        """Determine financial year"""
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
            if date.month >= 4:
                return f"FY{date.year % 100}"
            else:
                return f"FY{(date.year - 1) % 100}"
        except:
            return f"FY{datetime.now().year % 100}"