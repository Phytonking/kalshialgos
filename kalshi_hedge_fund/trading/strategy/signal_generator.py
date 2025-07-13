"""
Signal Generator for Trading Decisions

This module generates trading signals based on analysis results from
LLM reasoning and statistical analysis.
"""

import asyncio
from typing import Dict, Any, List, Optional
import numpy as np

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals based on analysis results
    
    Combines LLM analysis and statistical analysis to generate
    actionable trading signals with confidence levels.
    """
    
    def __init__(self, config):
        """
        Initialize the signal generator
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.min_confidence = config.min_confidence_threshold
        
        # Signal thresholds
        self.buy_threshold = 0.6  # 60% probability for buy signal
        self.sell_threshold = 0.4  # 40% probability for sell signal
        self.hold_threshold = 0.1  # 10% confidence difference for hold
        
        logger.info("Signal Generator initialized")
    
    async def generate_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate trading signal from analysis results
        
        Args:
            analysis: Analysis results dictionary containing LLM and statistical analysis
            
        Returns:
            Trading signal dictionary
        """
        try:
            logger.info("Generating trading signal from analysis")
            
            # Extract analysis components
            llm_analysis = analysis.get("llm_analysis", {})
            statistical_analysis = analysis.get("statistical_analysis", {})
            
            # Generate signals from different sources
            signals = {}
            
            # LLM-based signal
            if llm_analysis:
                signals["llm"] = self._generate_llm_signal(llm_analysis)
            
            # Statistical signal
            if statistical_analysis:
                signals["statistical"] = self._generate_statistical_signal(statistical_analysis)
            
            # Combine signals
            combined_signal = self._combine_signals(signals, analysis)
            
            logger.info(f"Generated signal: {combined_signal.get('action', 'UNKNOWN')}")
            return combined_signal
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return self._fallback_signal(analysis)
    
    def _generate_llm_signal(self, llm_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal from LLM analysis"""
        try:
            analysis_data = llm_analysis.get("analysis", {})
            
            # Extract trading recommendations
            recommendations = analysis_data.get("trading_recommendations", [])
            
            if not recommendations:
                return {"action": "HOLD", "confidence": 0.0, "reason": "No LLM recommendations"}
            
            # Find the highest confidence recommendation
            best_recommendation = max(recommendations, key=lambda x: x.get("confidence", 0))
            
            return {
                "action": best_recommendation.get("action", "HOLD"),
                "confidence": best_recommendation.get("confidence", 0.0),
                "reason": best_recommendation.get("reasoning", "LLM recommendation"),
                "source": "llm"
            }
            
        except Exception as e:
            logger.error(f"LLM signal generation failed: {e}")
            return {"action": "HOLD", "confidence": 0.0, "reason": f"LLM error: {e}"}
    
    def _generate_statistical_signal(self, statistical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate signal from statistical analysis"""
        try:
            # Extract ensemble probability
            ensemble_prob = statistical_analysis.get("ensemble_probability", 0.5)
            ensemble_confidence = statistical_analysis.get("ensemble_confidence", 0.0)
            
            # Determine action based on probability
            if ensemble_prob > self.buy_threshold:
                action = "BUY"
                confidence = ensemble_confidence * (ensemble_prob - 0.5) * 2
            elif ensemble_prob < self.sell_threshold:
                action = "SELL"
                confidence = ensemble_confidence * (0.5 - ensemble_prob) * 2
            else:
                action = "HOLD"
                confidence = ensemble_confidence * 0.5
            
            return {
                "action": action,
                "confidence": min(confidence, 1.0),
                "probability": ensemble_prob,
                "reason": f"Statistical probability: {ensemble_prob:.2f}",
                "source": "statistical"
            }
            
        except Exception as e:
            logger.error(f"Statistical signal generation failed: {e}")
            return {"action": "HOLD", "confidence": 0.0, "reason": f"Statistical error: {e}"}
    
    def _combine_signals(self, signals: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Combine signals from different sources"""
        try:
            if not signals:
                return {"action": "HOLD", "confidence": 0.0, "reason": "No signals available"}
            
            # Weight the signals
            weights = {
                "llm": 0.6,  # LLM gets higher weight
                "statistical": 0.4
            }
            
            combined_action = "HOLD"
            combined_confidence = 0.0
            total_weight = 0.0
            reasons = []
            
            for source, signal in signals.items():
                if source in weights:
                    weight = weights[source]
                    total_weight += weight
                    
                    # Convert actions to numerical values for averaging
                    action_value = self._action_to_value(signal.get("action", "HOLD"))
                    confidence = signal.get("confidence", 0.0)
                    
                    combined_confidence += confidence * weight
                    reasons.append(f"{source}: {signal.get('reason', 'No reason')}")
            
            # Normalize confidence
            if total_weight > 0:
                combined_confidence /= total_weight
            
            # Convert back to action
            combined_action = self._value_to_action(combined_confidence)
            
            # Apply confidence threshold
            if combined_confidence < self.min_confidence:
                combined_action = "HOLD"
                reasons.append("Below confidence threshold")
            
            return {
                "action": combined_action,
                "confidence": combined_confidence,
                "reasons": reasons,
                "individual_signals": signals,
                "weights_used": weights,
                "contract_id": analysis.get("contract_id"),
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"Signal combination failed: {e}")
            return {"action": "HOLD", "confidence": 0.0, "reason": f"Combination error: {e}"}
    
    def _action_to_value(self, action: str) -> float:
        """Convert action to numerical value"""
        action_map = {
            "BUY": 1.0,
            "HOLD": 0.5,
            "SELL": 0.0
        }
        return action_map.get(action.upper(), 0.5)
    
    def _value_to_action(self, value: float) -> str:
        """Convert numerical value back to action"""
        if value > 0.6:
            return "BUY"
        elif value < 0.4:
            return "SELL"
        else:
            return "HOLD"
    
    def _fallback_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback signal when generation fails"""
        return {
            "action": "HOLD",
            "confidence": 0.0,
            "reason": "Signal generation failed",
            "contract_id": analysis.get("contract_id"),
            "timestamp": asyncio.get_event_loop().time()
        }
    
    def validate_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Validate a trading signal
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            True if signal is valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ["action", "confidence"]
            for field in required_fields:
                if field not in signal:
                    logger.warning(f"Signal missing required field: {field}")
                    return False
            
            # Validate action
            valid_actions = ["BUY", "SELL", "HOLD"]
            if signal["action"] not in valid_actions:
                logger.warning(f"Invalid action: {signal['action']}")
                return False
            
            # Validate confidence
            confidence = signal["confidence"]
            if not (0.0 <= confidence <= 1.0):
                logger.warning(f"Invalid confidence: {confidence}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Signal validation failed: {e}")
            return False