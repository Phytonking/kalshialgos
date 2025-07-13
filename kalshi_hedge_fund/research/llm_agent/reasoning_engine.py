"""
LLM Reasoning Engine for Kalshi Event Analysis

This module provides LLM-powered reasoning capabilities for analyzing
Kalshi event contracts and generating trading insights.
"""

import asyncio
from typing import Dict, Any, List, Optional
import json

try:
    import openai
except ImportError:
    openai = None

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class LLMReasoningEngine:
    """
    LLM-powered reasoning engine for market analysis
    
    Uses OpenAI's GPT models to analyze event contracts, generate research
    questions, and provide trading insights.
    """
    
    def __init__(self, config):
        """
        Initialize the LLM reasoning engine
        
        Args:
            config: Configuration object containing OpenAI API settings
        """
        self.config = config
        self.model = config.llm_model
        
        if openai is None:
            logger.warning("OpenAI library not available. LLM features will be disabled.")
            self.client = None
        else:
            self.client = openai.AsyncOpenAI(
                api_key=config.openai_api_key,
                organization=config.openai_organization
            )
        
        # System prompts for different analysis types
        self.system_prompts = {
            "event_analysis": """You are an expert financial analyst specializing in event-driven trading on prediction markets. 
            Analyze the given Kalshi event contract and provide insights on:
            1. Event probability assessment
            2. Key factors that could influence the outcome
            3. Market sentiment analysis
            4. Risk factors and uncertainties
            5. Trading recommendations
            
            Be objective, data-driven, and consider multiple scenarios.""",
            
            "research_planning": """You are a research strategist for a quantitative hedge fund.
            Given an event contract, create a comprehensive research plan that includes:
            1. Key information needs
            2. Data sources to investigate
            3. Timeline for research
            4. Priority research tasks
            5. Success metrics
            
            Focus on actionable insights that can inform trading decisions.""",
            
            "fact_checking": """You are a fact-checking specialist for financial markets.
            Verify the accuracy and reliability of information related to the event contract.
            Consider:
            1. Source credibility
            2. Information recency
            3. Potential biases
            4. Conflicting information
            5. Confidence level in the information
            
            Provide a confidence score and reasoning for your assessment."""
        }
        
        logger.info("LLM Reasoning Engine initialized")
    
    async def analyze_event(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive LLM analysis of an event contract
        
        Args:
            contract: Contract information dictionary
            
        Returns:
            Analysis results dictionary
        """
        if self.client is None:
            return self._fallback_analysis(contract)
        
        try:
            logger.info(f"Starting LLM analysis for contract: {contract.get('id', 'unknown')}")
            
            # Extract contract information
            contract_info = self._extract_contract_info(contract)
            
            # Generate analysis prompt
            prompt = self._create_analysis_prompt(contract_info)
            
            # Get LLM response
            response = await self._get_llm_response(
                prompt, 
                system_prompt=self.system_prompts["event_analysis"]
            )
            
            # Parse and structure the response
            analysis = self._parse_analysis_response(response, contract)
            
            logger.info(f"LLM analysis completed for contract: {contract.get('id', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return self._fallback_analysis(contract)
    
    async def generate_research_plan(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a research plan for an event contract
        
        Args:
            contract: Contract information dictionary
            
        Returns:
            Research plan dictionary
        """
        if self.client is None:
            return self._fallback_research_plan(contract)
        
        try:
            contract_info = self._extract_contract_info(contract)
            prompt = self._create_research_prompt(contract_info)
            
            response = await self._get_llm_response(
                prompt,
                system_prompt=self.system_prompts["research_planning"]
            )
            
            return self._parse_research_plan(response, contract)
            
        except Exception as e:
            logger.error(f"Research plan generation failed: {e}")
            return self._fallback_research_plan(contract)
    
    async def fact_check_information(self, information: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fact-check information related to an event
        
        Args:
            information: Information to fact-check
            context: Context about the event
            
        Returns:
            Fact-checking results
        """
        if self.client is None:
            return self._fallback_fact_check(information, context)
        
        try:
            prompt = f"""
            Information to fact-check: {information}
            
            Event context: {json.dumps(context, indent=2)}
            
            Please fact-check this information and provide:
            1. Credibility assessment
            2. Confidence score (0-1)
            3. Reasoning
            4. Potential biases or issues
            5. Recommendations
            """
            
            response = await self._get_llm_response(
                prompt,
                system_prompt=self.system_prompts["fact_checking"]
            )
            
            return self._parse_fact_check_response(response)
            
        except Exception as e:
            logger.error(f"Fact-checking failed: {e}")
            return self._fallback_fact_check(information, context)
    
    def _extract_contract_info(self, contract: Dict[str, Any]) -> str:
        """Extract relevant information from contract for analysis"""
        info_parts = []
        
        if "title" in contract:
            info_parts.append(f"Title: {contract['title']}")
        
        if "description" in contract:
            info_parts.append(f"Description: {contract['description']}")
        
        if "outcomes" in contract:
            info_parts.append(f"Outcomes: {json.dumps(contract['outcomes'], indent=2)}")
        
        if "expiration_date" in contract:
            info_parts.append(f"Expiration: {contract['expiration_date']}")
        
        if "current_price" in contract:
            info_parts.append(f"Current Price: {contract['current_price']}")
        
        return "\n".join(info_parts)
    
    def _create_analysis_prompt(self, contract_info: str) -> str:
        """Create prompt for event analysis"""
        return f"""
        Please analyze the following Kalshi event contract:
        
        {contract_info}
        
        Provide a comprehensive analysis including:
        1. Probability assessment for each outcome
        2. Key factors that could influence the result
        3. Market sentiment analysis
        4. Risk factors and uncertainties
        5. Trading recommendations with confidence levels
        6. Timeline considerations
        7. Related events or correlations to monitor
        
        Format your response as JSON with the following structure:
        {{
            "probability_assessment": {{
                "outcome_1": {{"probability": 0.0, "confidence": 0.0, "reasoning": ""}},
                "outcome_2": {{"probability": 0.0, "confidence": 0.0, "reasoning": ""}}
            }},
            "key_factors": ["factor1", "factor2"],
            "market_sentiment": "bullish/bearish/neutral",
            "risk_factors": ["risk1", "risk2"],
            "trading_recommendations": [
                {{
                    "action": "BUY/SELL/HOLD",
                    "outcome": "outcome_name",
                    "confidence": 0.0,
                    "reasoning": ""
                }}
            ],
            "timeline_considerations": "text",
            "related_events": ["event1", "event2"]
        }}
        """
    
    def _create_research_prompt(self, contract_info: str) -> str:
        """Create prompt for research planning"""
        return f"""
        Create a research plan for the following event contract:
        
        {contract_info}
        
        Provide a structured research plan including:
        1. Key information needs
        2. Data sources to investigate
        3. Timeline for research
        4. Priority research tasks
        5. Success metrics
        
        Format your response as JSON with the following structure:
        {{
            "information_needs": ["need1", "need2"],
            "data_sources": ["source1", "source2"],
            "timeline": {{
                "immediate": ["task1", "task2"],
                "short_term": ["task1", "task2"],
                "ongoing": ["task1", "task2"]
            }},
            "priority_tasks": ["task1", "task2"],
            "success_metrics": ["metric1", "metric2"]
        }}
        """
    
    async def _get_llm_response(self, prompt: str, system_prompt: str) -> str:
        """Get response from LLM"""
        if self.client is None:
            raise RuntimeError("OpenAI client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def _parse_analysis_response(self, response: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM analysis response"""
        try:
            # Try to parse as JSON
            if response.strip().startswith("{"):
                parsed = json.loads(response)
            else:
                # Fallback parsing for non-JSON responses
                parsed = self._parse_text_response(response)
            
            return {
                "contract_id": contract.get("id"),
                "analysis": parsed,
                "timestamp": asyncio.get_event_loop().time(),
                "model": self.model
            }
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON, using text parsing")
            return {
                "contract_id": contract.get("id"),
                "analysis": self._parse_text_response(response),
                "timestamp": asyncio.get_event_loop().time(),
                "model": self.model
            }
    
    def _parse_text_response(self, response: str) -> Dict[str, Any]:
        """Parse text response when JSON parsing fails"""
        return {
            "raw_response": response,
            "probability_assessment": {},
            "key_factors": [],
            "market_sentiment": "neutral",
            "risk_factors": [],
            "trading_recommendations": [],
            "timeline_considerations": "",
            "related_events": []
        }
    
    def _parse_research_plan(self, response: str, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Parse research plan response"""
        try:
            if response.strip().startswith("{"):
                parsed = json.loads(response)
            else:
                parsed = {"raw_response": response}
            
            return {
                "contract_id": contract.get("id"),
                "research_plan": parsed,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except json.JSONDecodeError:
            return {
                "contract_id": contract.get("id"),
                "research_plan": {"raw_response": response},
                "timestamp": asyncio.get_event_loop().time()
            }
    
    def _parse_fact_check_response(self, response: str) -> Dict[str, Any]:
        """Parse fact-checking response"""
        return {
            "raw_response": response,
            "credibility": "unknown",
            "confidence": 0.5,
            "reasoning": "",
            "biases": [],
            "recommendations": []
        }
    
    def _fallback_analysis(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when LLM is not available"""
        return {
            "contract_id": contract.get("id"),
            "analysis": {
                "probability_assessment": {},
                "key_factors": ["LLM analysis not available"],
                "market_sentiment": "neutral",
                "risk_factors": ["Limited analysis capability"],
                "trading_recommendations": [],
                "timeline_considerations": "Manual analysis required",
                "related_events": []
            },
            "timestamp": asyncio.get_event_loop().time(),
            "model": "fallback"
        }
    
    def _fallback_research_plan(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback research plan when LLM is not available"""
        return {
            "contract_id": contract.get("id"),
            "research_plan": {
                "information_needs": ["Manual research required"],
                "data_sources": ["Kalshi API", "News sources"],
                "timeline": {"immediate": [], "short_term": [], "ongoing": []},
                "priority_tasks": ["Manual analysis"],
                "success_metrics": ["Manual assessment"]
            },
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def _fallback_fact_check(self, information: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback fact-checking when LLM is not available"""
        return {
            "raw_response": "Fact-checking not available",
            "credibility": "unknown",
            "confidence": 0.0,
            "reasoning": "LLM fact-checking not available",
            "biases": [],
            "recommendations": ["Manual verification required"]
        }