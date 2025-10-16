from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
from typing import Optional

from agents.orchestrator import AgentOrchestrator
from agents.scraper_agent import DateScraperAgent
from agents.fetcher_agent import PDFFetcherAgent
from agents.parser_agent import ParserAgent
from agents.analyzer_agent import AnalyzerAgent

app = FastAPI(title="Market Khabri API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Pydantic models
class Company(BaseModel):
    symbol: str
    name: str

class ResultDate(BaseModel):
    company_symbol: str
    company_name: str
    result_date: str
    quarter: str
    financial_year: str

class FinancialMetrics(BaseModel):
    revenue: Optional[float]
    profit_after_tax: Optional[float]
    eps: Optional[float]
    operating_margin: Optional[float]
    yoy_growth: Optional[float]
    qoq_growth: Optional[float]

class AnalysisResult(BaseModel):
    company_symbol: str
    company_name: str
    quarter: str
    financial_year: str
    metrics: FinancialMetrics
    insights: str
    red_flags: List[str]
    highlights: List[str]
    analyzed_at: str

class ChatQuery(BaseModel):
    question: str
    company_symbol: Optional[str] = None



@app.get("/")
async def root():
    return {
        "message": "Market Khabri API - Your Personal Stock Market Intelligence",
        "status": "running",
        "endpoints": {
            "upcoming_results": "/api/upcoming-results",
            "analyze_company": "/api/analyze/{symbol}",
            "latest_results": "/api/latest-results",
            "chat": "/api/chat"
        }
    }

@app.get("/api/upcoming-results", response_model=List[ResultDate])
async def get_upcoming_results(limit: int = 20):
    """
    Fetch upcoming quarterly result dates from NSE/BSE
    """
    try:
        results = await orchestrator.get_upcoming_result_dates(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result dates: {str(e)}")

@app.post("/api/analyze/{symbol}", response_model=AnalysisResult)
async def analyze_company(symbol: str):
    """
    Trigger full analysis for a company:
    1. Fetch latest result PDF
    2. Parse financial data
    3. Generate AI insights
    """
    try:
        result = await orchestrator.analyze_company_results(symbol.upper())
        if not result:
            raise HTTPException(status_code=404, detail=f"No results found for {symbol}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/latest-results", response_model=List[AnalysisResult])
async def get_latest_results(limit: int = 10):
    """
    Get recently analyzed company results
    """
    try:
        results = await orchestrator.get_latest_analyzed_results(limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")

@app.post("/api/chat")
async def chat_with_ai(query: ChatQuery):
    """
    Conversational interface - ask questions about company results
    Example: "How did TCS perform this quarter?"
    """
    try:
        response = await orchestrator.handle_chat_query(query.question, query.company_symbol)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {
            "scraper": "active",
            "fetcher": "active",
            "parser": "active",
            "analyzer": "active"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)