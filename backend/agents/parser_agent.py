from dotenv import load_dotenv

load_dotenv()

import fitz  # PyMuPDF
import re
import random
from typing import Dict, Optional
from groq import Groq
import os


class ParserAgent:
    """
    Extracts structured financial data from PDFs using LLM + regex
    """
    
    def __init__(self):
        # Initialize Groq client (free tier)
        # Get API key from environment variable
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set. Using demo mode.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        
        self.model = "llama-3.3-70b-versatile"  # NEW - Fast & reliable
        
        # Demo data templates
        self.demo_data_templates = {
            "TCS": {
                "revenue": 62600, "pat": 12250, "eps": 33.4,
                "yoy_growth": 6.8, "margin": 19.6
            },
            "INFY": {
                "revenue": 40960, "pat": 6850, "eps": 16.7,
                "yoy_growth": 4.2, "margin": 16.7
            },
            "RELIANCE": {
                "revenue": 230000, "pat": 17800, "eps": 27.2,
                "yoy_growth": 12.1, "margin": 7.7
            },
            "WIPRO": {
                "revenue": 22650, "pat": 3050, "eps": 5.6,
                "yoy_growth": 3.5, "margin": 13.5
            }
        }
    
    async def parse_pdf(self, pdf_path: str, symbol: str) -> Optional[Dict]:
        """
        Parse PDF and extract financial metrics
        """
        # Check if demo mode
        if pdf_path.startswith("DEMO:"):
            print(f"📊 Using demo data for {symbol}")
            return self._generate_demo_data(symbol)
        
        # Try to parse real PDF
        try:
            text = self._extract_text_from_pdf(pdf_path)
            
            if not text:
                print("❌ Could not extract text from PDF")
                return self._generate_demo_data(symbol)
            
            # Use LLM to extract structured data
            if self.client:
                parsed = await self._parse_with_llm(text, symbol)
                if parsed:
                    return parsed
            
            # Fallback: regex extraction
            return self._parse_with_regex(text, symbol)
            
        except Exception as e:
            print(f"❌ Parsing error: {e}")
            return self._generate_demo_data(symbol)
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF using PyMuPDF
        """
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            # Extract from first 5 pages (financials usually on first pages)
            for page_num in range(min(5, len(doc))):
                page = doc[page_num]
                text += page.get_text()
            
            doc.close()
            return text
            
        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            return ""
    
    async def _parse_with_llm(self, text: str, symbol: str) -> Optional[Dict]:
        """
        Use Groq LLM to extract financial data
        """
        try:
            prompt = f"""Extract financial metrics from this quarterly result text:

{text[:3000]}

Extract and return ONLY these values in JSON format:
- revenue (in crores)
- profit_after_tax (in crores)
- eps (earnings per share)
- operating_margin (percentage)
- yoy_growth (year-over-year growth percentage)
- qoq_growth (quarter-over-quarter growth percentage)
- quarter (Q1/Q2/Q3/Q4)
- financial_year (e.g., FY24)

Return valid JSON only, no extra text."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial data extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            data = json.loads(result)
            data["company_name"] = self._get_company_name(symbol)
            
            print(f"✅ LLM parsed data for {symbol}")
            return data
            
        except Exception as e:
            print(f"⚠️ LLM parsing failed: {e}")
            return None
    
    def _parse_with_regex(self, text: str, symbol: str) -> Dict:
        """
        Fallback: Extract using regex patterns
        """
        data = {
            "company_name": self._get_company_name(symbol),
            "quarter": "Q4",
            "financial_year": "FY24"
        }
        
        # Revenue patterns
        revenue_patterns = [
            r'Total Income.*?(?:Rs\.|₹)\s*([\d,]+\.?\d*)\s*(?:crore|Cr)',
            r'Revenue.*?(?:Rs\.|₹)\s*([\d,]+\.?\d*)\s*(?:crore|Cr)',
        ]
        
        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["revenue"] = float(match.group(1).replace(',', ''))
                break
        
        # If regex fails, use demo data
        if "revenue" not in data:
            return self._generate_demo_data(symbol)
        
        return data
    
    def _generate_demo_data(self, symbol: str) -> Dict:
        """
        Generate realistic demo financial data
        """
        # Use template if available
        if symbol in self.demo_data_templates:
            template = self.demo_data_templates[symbol]
        else:
            # Generate random but realistic data
            template = {
                "revenue": random.randint(10000, 50000),
                "pat": random.randint(1000, 8000),
                "eps": round(random.uniform(5, 30), 2),
                "yoy_growth": round(random.uniform(-5, 15), 1),
                "margin": round(random.uniform(10, 25), 1)
            }
        
        # Add some variance (±5%)
        variance = 0.05
        
        return {
            "company_name": self._get_company_name(symbol),
            "quarter": "Q4",
            "financial_year": "FY24",
            "revenue": round(template["revenue"] * (1 + random.uniform(-variance, variance)), 2),
            "profit_after_tax": round(template["pat"] * (1 + random.uniform(-variance, variance)), 2),
            "eps": round(template["eps"] * (1 + random.uniform(-variance, variance)), 2),
            "operating_margin": round(template["margin"] * (1 + random.uniform(-variance, variance)), 2),
            "yoy_growth": round(template["yoy_growth"] * (1 + random.uniform(-variance, variance)), 2),
            "qoq_growth": round(random.uniform(-3, 8), 2)
        }
    
    def _get_company_name(self, symbol: str) -> str:
        """
        Get full company name from symbol
        """
        names = {
            "TCS": "Tata Consultancy Services",
            "INFY": "Infosys",
            "RELIANCE": "Reliance Industries",
            "WIPRO": "Wipro",
            "HDFCBANK": "HDFC Bank",
            "ICICIBANK": "ICICI Bank",
            "SBIN": "State Bank of India",
            "BHARTIARTL": "Bharti Airtel",
            "ITC": "ITC Limited",
            "KOTAKBANK": "Kotak Mahindra Bank",
            "LT": "Larsen & Toubro",
            "AXISBANK": "Axis Bank",
            "ASIANPAINT": "Asian Paints",
            "MARUTI": "Maruti Suzuki",
            "TITAN": "Titan Company"
        }
        return names.get(symbol, symbol)