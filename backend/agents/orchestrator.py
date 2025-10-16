import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import json
import os

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
    
    async def _triage_query(self, question: str) -> dict:
        """
        Uses a small, fast LLM to classify the query and extract a symbol.
        """
        prompt = f"""
        Analyze the user's query: "{question}"
        Your task is to classify this query into one of three categories and identify the stock symbol if possible.
        The categories are: REAL_STOCK, FAKE_STOCK, OFF_TOPIC.

        - If the query is about a real-world stock or company (e.g., "Reliance", "AAPL", "How is TCS doing?"), classify it as REAL_STOCK and extract the stock symbol.
        - If the query mentions a name that is clearly not a real stock ticker or company (e.g., "mihit", "harshilagro"), classify it as FAKE_STOCK.
        - If the query is unrelated to stocks, finance, or companies (e.g., "chicken biryani recipe"), classify it as OFF_TOPIC.

        Respond ONLY with a JSON object in the format: {{"query_type": "CATEGORY", "symbol": "EXTRACTED_SYMBOL_OR_NULL"}}
        """
        try:
            # Use a fast model for this classification task
            chat_completion = self.analyzer.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            response_json = json.loads(chat_completion.choices[0].message.content)
            return response_json
        except Exception as e:
            print(f"Error during query triage: {e}")
            # Default to a safe category in case of error
            return {"query_type": "OFF_TOPIC", "symbol": None}

    async def handle_chat_query(self, question: str, company_symbol: Optional[str] = None) -> str:
        """
        Handles chat queries with guardrails to prevent hallucination.
        """
        print(f"💬 Chat Query: {question}")
        
        # Step 1: Triage the query to understand its intent
        triage_result = await self._triage_query(question)
        query_type = triage_result.get("query_type")
        extracted_symbol = triage_result.get("symbol")
        
        # Step 2: Handle bad queries immediately
        if query_type == "FAKE_STOCK":
            return "I'm sorry, but that doesn't seem to be a real stock or company. I can only provide information on publicly listed entities."

        if query_type == "OFF_TOPIC":
            return "I am a financial analysis assistant and can only answer questions related to stocks and companies."

        # Step 3: For real stock queries, decide which data to use
        # Prioritize the symbol extracted from the question over the one from the frontend for accuracy
        final_symbol = extracted_symbol or company_symbol
        
        if not final_symbol:
            return "Could you please specify which company you're asking about?"
            
        context = None
        analysis = self._load_analysis(final_symbol) # Use your existing method
        
        if analysis:
            # Case A: We found an analysis file for this company
            print(f"✅ Found '{final_symbol}' in local context. Answering with specific data.")
            context = f"Latest analysis for {final_symbol}: {json.dumps(analysis)}"
        else:
            # Case B: No analysis file, but it's a real stock
            print(f"ℹ️ '{final_symbol}' not in local context. Answering with general knowledge.")
            # Context remains None

        # Step 4: Call the analyzer agent to get the final answer
        response = await self.analyzer.answer_question(question, context)
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