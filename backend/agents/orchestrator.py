import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import json
import os
import glob

from .scraper_agent import DateScraperAgent
from .fetcher_agent import PDFFetcherAgent
from .parser_agent import ParserAgent
from .analyzer_agent import AnalyzerAgent

class AgentOrchestrator:
    """
    Master orchestrator that coordinates all AI agents
    """
    def __init__(self):
        self.scraper = DateScraperAgent()
        self.fetcher = PDFFetcherAgent()
        self.parser = ParserAgent()
        self.analyzer = AnalyzerAgent()
        
        # Simple file-based storage (replace with DB in production)
        self.storage_path = "data"
        os.makedirs(self.storage_path, exist_ok=True)
        
    async def get_upcoming_result_dates(self, limit: int = 20) -> List[Dict]:
        """
        Step 1: Scrape upcoming result dates
        """
        print(f"🔍 Scraper Agent: Fetching upcoming result dates...")
        dates = await self.scraper.fetch_result_dates(limit)
        
        # Cache results
        self._save_to_cache("upcoming_dates.json", dates)
        
        return dates
    
    async def analyze_company_results(self, symbol: str) -> Optional[Dict]:
        """
        Full pipeline: Fetch → Parse → Analyze
        """
        print(f"\n🚀 Starting analysis for {symbol}...")
        
        # Step 1: Fetch PDF
        print(f"📥 Fetcher Agent: Downloading results for {symbol}...")
        pdf_path = await self.fetcher.fetch_result_pdf(symbol)
        
        if not pdf_path:
            print(f"❌ No PDF found for {symbol}")
            return None
        
        # Step 2: Parse PDF
        print(f"📑 Parser Agent: Extracting financials from PDF...")
        parsed_data = await self.parser.parse_pdf(pdf_path, symbol)
        
        if not parsed_data:
            print(f"❌ Failed to parse PDF for {symbol}")
            return None
        
        # Step 3: Generate insights
        print(f"🤖 Analyzer Agent: Generating AI insights...")
        analysis = await self.analyzer.analyze_financials(parsed_data, symbol)
        
        # Combine results
        result = {
            "company_symbol": symbol,
            "company_name": parsed_data.get("company_name", symbol),
            "quarter": parsed_data.get("quarter", "Q4"),
            "financial_year": parsed_data.get("financial_year", "FY24"),
            "metrics": {
                "revenue": parsed_data.get("revenue"),
                "profit_after_tax": parsed_data.get("profit_after_tax"),
                "eps": parsed_data.get("eps"),
                "operating_margin": parsed_data.get("operating_margin"),
                "yoy_growth": parsed_data.get("yoy_growth"),
                "qoq_growth": parsed_data.get("qoq_growth"),
            },
            "insights": analysis.get("insights", ""),
            "red_flags": analysis.get("red_flags", []),
            "highlights": analysis.get("highlights", []),
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Save to cache
        self._save_analysis(symbol, result)
        
        print(f"✅ Analysis complete for {symbol}!")
        return result
    
    async def get_latest_analyzed_results(self, limit: int = 10) -> List[Dict]:
        """
        Retrieve recently analyzed results from cache
        """
        analyses_path = os.path.join(self.storage_path, "analyses")
        if not os.path.exists(analyses_path):
            return []
        
        files = sorted(
            [f for f in os.listdir(analyses_path) if f.endswith('.json')],
            key=lambda x: os.path.getmtime(os.path.join(analyses_path, x)),
            reverse=True
        )[:limit]
        
        results = []
        for file in files:
            with open(os.path.join(analyses_path, file), 'r') as f:
                results.append(json.load(f))
        
        return results
    
    def _load_all_analyses_as_context(self) -> str:
        """
        Loads all available analyses from JSON files into a single string for context.
        """
        all_analyses = []
        analyses_path = os.path.join(self.storage_path, "analyses")
        if not os.path.exists(analyses_path):
            return "No specific company analysis data is available."

        analysis_files = glob.glob(os.path.join(analyses_path, '*.json'))
        for file_path in analysis_files:
            try:
                with open(file_path, 'r') as f:
                    all_analyses.append(json.load(f))
            except Exception as e:
                print(f"Warning: Could not load or parse {file_path}: {e}")
        
        if not all_analyses:
            return "No specific company analysis data is available."
        
        # Return the data as a JSON string
        return json.dumps(all_analyses, indent=2)

    async def handle_chat_query(self, messages: List[Dict]) -> str:
        """
        Handles the entire chat conversation by passing history and knowledge to the analyzer.
        (This signature now matches what main.py is sending)
        """
        print(f"💬 Handling chat with history of {len(messages)} messages...")
        
        # Step 1: Prepare the entire knowledge base from local files
        knowledge_base = self._load_all_analyses_as_context()
        
        # Step 2: Call the analyzer agent with the full history and knowledge base
        # NOTE: We must rename the function in analyzer_agent to match this
        response = await self.analyzer.answer_with_memory(messages, knowledge_base)
        return response
    
    def _save_to_cache(self, filename: str, data: any):
        """Save data to cache"""
        filepath = os.path.join(self.storage_path, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _save_analysis(self, symbol: str, data: Dict):
        """Save company analysis"""
        analyses_path = os.path.join(self.storage_path, "analyses")
        os.makedirs(analyses_path, exist_ok=True)
        
        filepath = os.path.join(analyses_path, f"{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_analysis(self, symbol: str) -> Optional[Dict]:
        """Load latest analysis for a company"""
        analyses_path = os.path.join(self.storage_path, "analyses")
        if not os.path.exists(analyses_path):
            return None
        
        files = [f for f in os.listdir(analyses_path) if f.startswith(symbol)]
        if not files:
            return None
        
        latest = sorted(files, reverse=True)[0]
        with open(os.path.join(analyses_path, latest), 'r') as f:
            return json.load(f)