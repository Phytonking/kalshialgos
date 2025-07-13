"""
Core Kalshi Hedge Fund Framework

This module contains the main KalshiHedgeFund class that orchestrates all components
of the AI-powered hedge fund framework.
"""

import asyncio
from typing import Dict, Any, Optional, List
from loguru import logger

from .config import Config
from .data.collectors.kalshi_api import KalshiAPICollector
from .research.llm_agent.reasoning_engine import LLMReasoningEngine
from .analysis.models.ensemble import EnsembleModel
from .trading.strategy.signal_generator import SignalGenerator
from .trading.execution.kalshi_trader import KalshiTrader
from .risk.monitors.exposure_monitor import ExposureMonitor
from .utils.logger import setup_logging


class KalshiHedgeFund:
    """
    Main class for the Kalshi AI Hedge Fund Framework
    
    This class orchestrates all components including data collection, research,
    analysis, trading, and risk management.
    """
    
    def __init__(self, config_path: Optional[str] = None, config: Optional[Config] = None):
        """
        Initialize the Kalshi Hedge Fund Framework
        
        Args:
            config_path: Path to configuration file
            config: Configuration object (if not using config_path)
        """
        # Load configuration
        if config is not None:
            self.config = config
        elif config_path is not None:
            self.config = Config.from_file(config_path)
        else:
            self.config = Config()
        
        # Setup logging
        setup_logging(
            level=self.config.log_level,
            log_file=self.config.log_file
        )
        
        logger.info("Initializing Kalshi AI Hedge Fund Framework")
        
        # Initialize components
        self._initialize_components()
        
        logger.info("Kalshi AI Hedge Fund Framework initialized successfully")
    
    def _initialize_components(self):
        """Initialize all framework components"""
        try:
            # Data collection
            self.kalshi_collector = KalshiAPICollector(self.config)
            
            # Research and analysis
            self.llm_engine = LLMReasoningEngine(self.config)
            self.ensemble_model = EnsembleModel(self.config)
            
            # Trading components
            self.signal_generator = SignalGenerator(self.config)
            self.kalshi_trader = KalshiTrader(self.config)
            
            # Connect trader to API collector
            self.kalshi_trader.set_api_collector(self.kalshi_collector)
            
            # Risk management
            self.exposure_monitor = ExposureMonitor(self.config)
            
            logger.info("All components initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise
    
    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Retrieve contract information from Kalshi
        
        Args:
            contract_id: The Kalshi contract ID
            
        Returns:
            Contract information dictionary
        """
        try:
            contract = await self.kalshi_collector.get_contract(contract_id)
            logger.info(f"Retrieved contract: {contract_id}")
            return contract
        except Exception as e:
            logger.error(f"Failed to retrieve contract {contract_id}: {e}")
            raise
    
    async def analyze_contract(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive analysis of a contract
        
        Args:
            contract: Contract information dictionary
            
        Returns:
            Analysis results dictionary
        """
        try:
            logger.info(f"Starting analysis for contract: {contract.get('id', 'unknown')}")
            
            # LLM-based research and reasoning
            llm_analysis = await self.llm_engine.analyze_event(contract)
            
            # Statistical analysis
            statistical_analysis = await self.ensemble_model.analyze_contract(contract)
            
            # Combine analyses
            analysis = {
                "contract_id": contract.get("id"),
                "llm_analysis": llm_analysis,
                "statistical_analysis": statistical_analysis,
                "timestamp": asyncio.get_event_loop().time(),
            }
            
            logger.info(f"Analysis completed for contract: {contract.get('id', 'unknown')}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze contract: {e}")
            raise
    
    async def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal based on analysis
        
        Args:
            analysis: Analysis results dictionary
            
        Returns:
            Trading signal dictionary
        """
        try:
            logger.info("Generating trading signal")
            
            signal = await self.signal_generator.generate_signal(analysis)
            
            # Apply risk checks
            if await self.exposure_monitor.check_signal(signal):
                logger.info("Signal passed risk checks")
                return signal
            else:
                logger.warning("Signal rejected by risk management")
                return {"action": "HOLD", "confidence": 0.0, "reason": "Risk limits exceeded"}
                
        except Exception as e:
            logger.error(f"Failed to generate signal: {e}")
            raise
    
    async def execute_trade(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute trade based on signal
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            Trade execution results
        """
        try:
            if signal.get("confidence", 0) < self.config.min_confidence_threshold:
                logger.info("Signal confidence below threshold, skipping execution")
                return {"status": "SKIPPED", "reason": "Low confidence"}
            
            logger.info(f"Executing trade: {signal}")
            
            # Execute the trade
            execution_result = await self.kalshi_trader.execute_signal(signal)
            
            # Update risk monitoring
            await self.exposure_monitor.update_positions(execution_result)
            
            logger.info(f"Trade executed successfully: {execution_result}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            raise
    
    async def run_strategy(self, contract_ids: List[str]) -> Dict[str, Any]:
        """
        Run the complete strategy for a list of contracts
        
        Args:
            contract_ids: List of contract IDs to analyze and trade
            
        Returns:
            Strategy execution results
        """
        try:
            logger.info(f"Running strategy for {len(contract_ids)} contracts")
            
            results = []
            for contract_id in contract_ids:
                try:
                    # Get contract
                    contract = await self.get_contract(contract_id)
                    
                    # Analyze contract
                    analysis = await self.analyze_contract(contract)
                    
                    # Generate signal
                    signal = await self.generate_signal(analysis)
                    
                    # Execute trade if signal is strong enough
                    if signal.get("confidence", 0) >= self.config.min_confidence_threshold:
                        execution = await self.execute_trade(signal)
                        results.append({
                            "contract_id": contract_id,
                            "analysis": analysis,
                            "signal": signal,
                            "execution": execution,
                        })
                    else:
                        results.append({
                            "contract_id": contract_id,
                            "analysis": analysis,
                            "signal": signal,
                            "execution": {"status": "SKIPPED", "reason": "Low confidence"},
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to process contract {contract_id}: {e}")
                    results.append({
                        "contract_id": contract_id,
                        "error": str(e),
                    })
            
            logger.info(f"Strategy completed for {len(contract_ids)} contracts")
            return {"results": results, "total_contracts": len(contract_ids)}
            
        except Exception as e:
            logger.error(f"Failed to run strategy: {e}")
            raise
    
    async def get_portfolio_status(self) -> Dict[str, Any]:
        """
        Get current portfolio status and performance
        
        Returns:
            Portfolio status dictionary
        """
        try:
            portfolio = await self.kalshi_trader.get_portfolio()
            risk_metrics = await self.exposure_monitor.get_risk_metrics()
            
            return {
                "portfolio": portfolio,
                "risk_metrics": risk_metrics,
                "timestamp": asyncio.get_event_loop().time(),
            }
        except Exception as e:
            logger.error(f"Failed to get portfolio status: {e}")
            raise
    
    async def shutdown(self):
        """Gracefully shutdown the framework"""
        try:
            logger.info("Shutting down Kalshi AI Hedge Fund Framework")
            
            # Close connections and cleanup
            await self.kalshi_collector.close()
            await self.kalshi_trader.close()
            
            logger.info("Framework shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            raise