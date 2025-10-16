from dotenv import load_dotenv

load_dotenv()

from groq import Groq
import os
from typing import Dict, List, Optional
import json

class AnalyzerAgent:
    """
    AI-powered financial analyst that generates insights
    """
    
    def __init__(self):
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            print("⚠️ GROQ_API_KEY not set. Using rule-based analysis.")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        
        self.model = "llama-3.3-70b-versatile"  # NEW - Fast & reliable
    
    async def analyze_financials(self, parsed_data: Dict, symbol: str) -> Dict:
        """
        Generate comprehensive financial analysis
        """
        if self.client:
            # Use LLM for deep analysis
            return await self._analyze_with_llm(parsed_data, symbol)
        else:
            # Fallback to rule-based analysis
            return self._analyze_with_rules(parsed_data, symbol)
    
    async def _analyze_with_llm(self, data: Dict, symbol: str) -> Dict:
        """
        Generate insights using Groq LLM
        """
        try:
            prompt = f"""You are a stock market analyst. Analyze these quarterly results and provide insights in a casual, engaging tone (like explaining to a friend):

Company: {data.get('company_name', symbol)}
Quarter: {data.get('quarter')} {data.get('financial_year')}

Financial Metrics:
- Revenue: ₹{data.get('revenue', 0):,.0f} Cr
- Profit After Tax: ₹{data.get('profit_after_tax', 0):,.0f} Cr
- EPS: ₹{data.get('eps', 0):.2f}
- Operating Margin: {data.get('operating_margin', 0):.1f}%
- YoY Growth: {data.get('yoy_growth', 0):.1f}%
- QoQ Growth: {data.get('qoq_growth', 0):.1f}%

Provide:
1. A 2-3 sentence summary of performance (casual tone, use words like "solid", "meh", "crushing it")
2. 3-4 key highlights (positive points)
3. 2-3 red flags or concerns (if any)

Format as JSON:
{{
  "insights": "summary text",
  "highlights": ["point 1", "point 2", ...],
  "red_flags": ["concern 1", "concern 2", ...]
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a street-smart stock analyst. Be concise, relatable, and honest."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0].strip()
            elif "```" in result:
                result = result.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(result)
            print(f"✅ LLM generated insights for {symbol}")
            return analysis
            
        except Exception as e:
            print(f"⚠️ LLM analysis failed: {e}, using rule-based fallback")
            return self._analyze_with_rules(data, symbol)
    
    def _analyze_with_rules(self, data: Dict, symbol: str) -> Dict:
        """
        Rule-based analysis fallback
        """
        revenue = data.get('revenue', 0)
        pat = data.get('profit_after_tax', 0)
        yoy = data.get('yoy_growth', 0)
        margin = data.get('operating_margin', 0)
        eps = data.get('eps', 0)
        
        # Generate insights
        insights = self._generate_insights_text(symbol, revenue, yoy, margin)
        highlights = self._generate_highlights(yoy, margin, eps, revenue)
        red_flags = self._generate_red_flags(yoy, margin, pat)
        
        return {
            "insights": insights,
            "highlights": highlights,
            "red_flags": red_flags
        }
    
    def _generate_insights_text(self, symbol: str, revenue: float, yoy: float, margin: float) -> str:
        """
        Generate main insights text
        """
        if yoy > 15:
            performance = "absolutely crushing it"
        elif yoy > 8:
            performance = "performing solidly"
        elif yoy > 3:
            performance = "showing steady growth"
        elif yoy > 0:
            performance = "growing but at a slower pace"
        else:
            performance = "facing headwinds"
        
        return f"{symbol} is {performance} this quarter with ₹{revenue:,.0f} Cr in revenue ({yoy:+.1f}% YoY). Operating margins at {margin:.1f}% show {'strong' if margin > 18 else 'decent' if margin > 12 else 'tight'} operational efficiency. {'Bulls are happy! 🚀' if yoy > 10 else 'Not bad, but room for improvement.' if yoy > 3 else 'Bears might be lurking. 🐻'}"
    
    def _generate_highlights(self, yoy: float, margin: float, eps: float, revenue: float) -> List[str]:
        """
        Generate positive highlights
        """
        highlights = []
        
        if yoy > 10:
            highlights.append(f"Strong double-digit YoY growth of {yoy:.1f}% - momentum is real!")
        elif yoy > 5:
            highlights.append(f"Healthy growth trajectory with {yoy:.1f}% YoY increase")
        elif yoy > 0:
            highlights.append(f"Maintaining positive growth at {yoy:.1f}% YoY despite market conditions")
        
        if margin > 20:
            highlights.append(f"Excellent operating margins at {margin:.1f}% - pricing power on display")
        elif margin > 15:
            highlights.append(f"Solid margins of {margin:.1f}% showing operational discipline")
        
        if eps > 25:
            highlights.append(f"Impressive EPS of ₹{eps:.2f} - shareholders eating good!")
        elif eps > 15:
            highlights.append(f"Decent EPS of ₹{eps:.2f} maintaining shareholder value")
        
        if revenue > 50000:
            highlights.append("Massive scale with revenue crossing ₹50,000 Cr - market leader vibes")
        elif revenue > 20000:
            highlights.append("Strong revenue base showing market presence")
        
        # Ensure at least 2 highlights
        if len(highlights) < 2:
            highlights.append("Company delivering on expectations this quarter")
        
        return highlights[:4]  # Max 4 highlights
    
    def _generate_red_flags(self, yoy: float, margin: float, pat: float) -> List[str]:
        """
        Generate concerns/red flags
        """
        red_flags = []
        
        if yoy < 0:
            red_flags.append(f"Negative YoY growth of {yoy:.1f}% - revenues declining, not good fam")
        elif yoy < 3:
            red_flags.append(f"Sluggish growth at {yoy:.1f}% - needs to pick up pace")
        
        if margin < 10:
            red_flags.append(f"Low margins at {margin:.1f}% - profitability under pressure")
        elif margin < 15:
            red_flags.append(f"Margins at {margin:.1f}% could be better - watch operational costs")
        
        if pat < 1000:
            red_flags.append("Profit levels are concerning - needs stronger bottom line")
        
        # If no red flags, add a neutral observation
        if len(red_flags) == 0:
            red_flags.append("Nothing major to worry about, but keep an eye on market trends")
        
        return red_flags[:3]  # Max 3 red flags
    
    async def answer_with_memory(self, messages: List[Dict], knowledge_base: str) -> str:
        """
        Answers a user's question using a single, comprehensive prompt with rules,
        conversation history, and a knowledge base.
        """
        if not self.client:
            return "Chat feature requires Groq API key. Please set GROQ_API_KEY environment variable."

        # This is the system prompt that controls all AI behavior
        system_prompt = f"""
        You are 'Khabri', an AI financial assistant. Your purpose is to be helpful, accurate, and safe.

        **STRICT BEHAVIORAL RULES:**
        1.  **SINGLE SOURCE OF TRUTH:** Your only source for specific company performance data (revenue, profit, etc.) is the JSON provided in the 'KNOWLEDGE BASE'. You MUST **NEVER** invent numbers or metrics. Quote the numbers exactly as they are.
        2.  **CONVERSATION MEMORY:** Maintain context using the 'CHAT HISTORY'. Your response should follow naturally from the last user query.
        3.  **NO FINANCIAL ADVICE:** You MUST NOT give any investment advice. Do not suggest buying, selling, or holding.
        4.  **STAY ON TOPIC:** You are a financial assistant. Politely decline any requests unrelated to finance, stocks, or business.

        **QUERY HANDLING LOGIC:**
        -   **IF** the user asks about a company found in the 'KNOWLEDGE BASE', base your answer strictly on the JSON data provided for that company.
        -   **IF** the user asks about a real company that is NOT in the 'KNOWLEDGE BASE', provide a brief, factual summary from your general knowledge. Start your response with "Based on general public information...".
        -   **IF** the user's query seems to refer to a name that is not a real company or stock (e.g., a person's name), politely state that you can only provide information on real companies.
        -   **IF** the query is off-topic, state your purpose: "I am a financial assistant and can only answer questions related to stocks and companies."

        **KNOWLEDGE BASE (Your specific data):**
        ```json
        {knowledge_base}
        ```

        Now, continue the conversation based on the CHAT HISTORY. The last message is the user's most recent question.
        """

        # Prepend the system prompt to the message history for the API call
        api_messages = [{"role": "system", "content": system_prompt}] + messages

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # A powerful model is needed to follow complex instructions
                messages=api_messages,
                temperature=0.2, # Lower temperature to reduce hallucination and be more factual
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Couldn't process that question right now. Try again! Error: {str(e)}"