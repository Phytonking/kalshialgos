"""
Exposure Monitor for Risk Management

This module monitors portfolio exposure, position limits, and risk metrics
to ensure the trading strategy stays within acceptable risk parameters.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import numpy as np

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ExposureMonitor:
    """
    Monitors portfolio exposure and risk metrics
    
    Tracks position sizes, correlations, drawdowns, and other risk metrics
    to ensure the portfolio stays within acceptable risk limits.
    """
    
    def __init__(self, config):
        """
        Initialize the exposure monitor
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.positions = {}
        self.risk_limits = config.get_risk_limits()
        self.risk_history = []
        self.alerts = []
        
        logger.info("Exposure Monitor initialized")
    
    async def check_signal(self, signal: Dict[str, Any]) -> bool:
        """
        Check if a trading signal passes risk management checks
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            True if signal passes risk checks, False otherwise
        """
        try:
            logger.info("Checking signal against risk limits")
            
            # Get current portfolio state
            portfolio = await self._get_current_portfolio()
            
            # Check various risk metrics
            checks = {}
            
            # Position size check
            checks["position_size"] = self._check_position_size(signal, portfolio)
            
            # Portfolio concentration check
            checks["concentration"] = self._check_concentration(signal, portfolio)
            
            # Correlation check
            checks["correlation"] = await self._check_correlation(signal, portfolio)
            
            # Drawdown check
            checks["drawdown"] = self._check_drawdown(portfolio)
            
            # Overall risk assessment
            all_passed = all(checks.values())
            
            if not all_passed:
                failed_checks = [k for k, v in checks.items() if not v]
                logger.warning(f"Signal failed risk checks: {failed_checks}")
                self._add_alert("RISK_LIMIT_EXCEEDED", f"Failed checks: {failed_checks}")
            
            return all_passed
            
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return False
    
    def _check_position_size(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check if position size is within limits"""
        try:
            portfolio_value = portfolio.get("total_value", 0.0)
            
            if portfolio_value <= 0:
                return False
            
            # Calculate proposed position size
            proposed_size = portfolio_value * self.config.max_position_size
            
            # Adjust for signal confidence
            confidence = signal.get("confidence", 0.0)
            adjusted_size = proposed_size * confidence
            
            # Check against limit
            max_allowed = portfolio_value * self.risk_limits["max_position_size"]
            
            is_within_limit = adjusted_size <= max_allowed
            
            if not is_within_limit:
                logger.warning(f"Position size {adjusted_size:.2f} exceeds limit {max_allowed:.2f}")
            
            return is_within_limit
            
        except Exception as e:
            logger.error(f"Position size check failed: {e}")
            return False
    
    def _check_concentration(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check portfolio concentration limits"""
        try:
            contract_id = signal.get("contract_id")
            if not contract_id:
                return True
            
            positions = portfolio.get("positions", [])
            
            # Calculate current exposure to this contract
            current_exposure = 0.0
            for position in positions:
                if position.get("contract_id") == contract_id:
                    current_exposure += abs(float(position.get("size", 0.0)))
            
            # Check if adding this position would exceed concentration limit
            portfolio_value = portfolio.get("total_value", 0.0)
            if portfolio_value > 0:
                concentration = current_exposure / portfolio_value
                max_concentration = self.risk_limits["max_position_size"] * 2  # Allow some flexibility
                
                return concentration <= max_concentration
            
            return True
            
        except Exception as e:
            logger.error(f"Concentration check failed: {e}")
            return False
    
    async def _check_correlation(self, signal: Dict[str, Any], portfolio: Dict[str, Any]) -> bool:
        """Check correlation with existing positions"""
        try:
            # This is a simplified correlation check
            # In practice, you'd calculate actual correlations between contracts
            
            positions = portfolio.get("positions", [])
            
            if len(positions) == 0:
                return True
            
            # For now, we'll use a simple heuristic
            # If we have many positions, assume some correlation risk
            num_positions = len(positions)
            max_positions = 20  # Arbitrary limit
            
            if num_positions >= max_positions:
                logger.warning(f"High number of positions: {num_positions}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Correlation check failed: {e}")
            return False
    
    def _check_drawdown(self, portfolio: Dict[str, Any]) -> bool:
        """Check if portfolio is within drawdown limits"""
        try:
            # Calculate current drawdown
            current_value = portfolio.get("total_value", 0.0)
            
            # Get peak value from history
            if self.risk_history:
                peak_value = max([entry.get("total_value", 0.0) for entry in self.risk_history])
                if peak_value > 0:
                    drawdown = (peak_value - current_value) / peak_value
                    
                    max_drawdown = self.risk_limits["max_drawdown"]
                    
                    if drawdown > max_drawdown:
                        logger.warning(f"Drawdown {drawdown:.2%} exceeds limit {max_drawdown:.2%}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Drawdown check failed: {e}")
            return False
    
    async def update_positions(self, execution_result: Dict[str, Any]):
        """Update position tracking after trade execution"""
        try:
            if execution_result.get("status") == "EXECUTED":
                contract_id = execution_result["contract_id"]
                action = execution_result["action"]
                size = execution_result["size"]
                
                # Update internal position tracking
                if contract_id not in self.positions:
                    self.positions[contract_id] = 0.0
                
                if action == "BUY":
                    self.positions[contract_id] += size
                else:  # SELL
                    self.positions[contract_id] -= size
                
                logger.info(f"Updated position tracking for {contract_id}: {self.positions[contract_id]}")
                
        except Exception as e:
            logger.error(f"Position update failed: {e}")
    
    async def get_risk_metrics(self) -> Dict[str, Any]:
        """
        Get current risk metrics
        
        Returns:
            Risk metrics dictionary
        """
        try:
            portfolio = await self._get_current_portfolio()
            
            # Calculate various risk metrics
            metrics = {}
            
            # Portfolio value
            metrics["total_value"] = portfolio.get("total_value", 0.0)
            
            # Number of positions
            positions = portfolio.get("positions", [])
            metrics["num_positions"] = len(positions)
            
            # Largest position
            if positions:
                largest_position = max(positions, key=lambda x: abs(float(x.get("size", 0.0))))
                metrics["largest_position"] = {
                    "contract_id": largest_position.get("contract_id"),
                    "size": float(largest_position.get("size", 0.0))
                }
            
            # Portfolio concentration
            if metrics["total_value"] > 0:
                total_exposure = sum(abs(float(p.get("size", 0.0))) for p in positions)
                metrics["concentration"] = total_exposure / metrics["total_value"]
            else:
                metrics["concentration"] = 0.0
            
            # Drawdown calculation
            if self.risk_history:
                peak_value = max([entry.get("total_value", 0.0) for entry in self.risk_history])
                if peak_value > 0:
                    metrics["drawdown"] = (peak_value - metrics["total_value"]) / peak_value
                else:
                    metrics["drawdown"] = 0.0
            else:
                metrics["drawdown"] = 0.0
            
            # Risk limits status
            metrics["risk_limits"] = {
                "max_position_size": self.risk_limits["max_position_size"],
                "max_drawdown": self.risk_limits["max_drawdown"],
                "var_limit": self.risk_limits["var_limit"]
            }
            
            # Add timestamp
            metrics["timestamp"] = datetime.now().isoformat()
            
            # Store in history
            self.risk_history.append(metrics)
            
            # Keep only recent history (last 100 entries)
            if len(self.risk_history) > 100:
                self.risk_history = self.risk_history[-100:]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Risk metrics calculation failed: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_current_portfolio(self) -> Dict[str, Any]:
        """Get current portfolio state"""
        # This would typically get data from the trader
        # For now, return a simulated portfolio
        return {
            "total_value": 10000.0,
            "positions": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def _add_alert(self, alert_type: str, message: str):
        """Add a risk alert"""
        alert = {
            "type": alert_type,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.alerts.append(alert)
        
        # Keep only recent alerts (last 50)
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
        
        logger.warning(f"Risk alert: {alert_type} - {message}")
    
    def get_alerts(self, alert_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get risk alerts
        
        Args:
            alert_type: Optional filter for alert type
            
        Returns:
            List of alert dictionaries
        """
        if alert_type:
            return [alert for alert in self.alerts if alert["type"] == alert_type]
        else:
            return self.alerts.copy()
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        logger.info("All risk alerts cleared")