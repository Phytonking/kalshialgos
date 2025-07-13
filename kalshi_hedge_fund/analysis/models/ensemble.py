"""
Ensemble Model for Kalshi Contract Analysis

This module provides ensemble methods for combining multiple analysis approaches
including statistical models, machine learning, and time series analysis.
"""

import asyncio
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class EnsembleModel:
    """
    Ensemble model for contract analysis
    
    Combines multiple analysis approaches including:
    - Statistical models
    - Machine learning models
    - Time series analysis
    - Market sentiment analysis
    """
    
    def __init__(self, config):
        """
        Initialize the ensemble model
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.models = {}
        self.scaler = None
        
        # Initialize models if sklearn is available
        if SKLEARN_AVAILABLE:
            self._initialize_ml_models()
        
        logger.info("Ensemble Model initialized")
    
    def _initialize_ml_models(self):
        """Initialize machine learning models"""
        self.models["random_forest"] = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.models["linear_regression"] = LinearRegression()
        self.scaler = StandardScaler()
        
        logger.info("Machine learning models initialized")
    
    async def analyze_contract(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive contract analysis using ensemble methods
        
        Args:
            contract: Contract information dictionary
            
        Returns:
            Analysis results dictionary
        """
        try:
            logger.info(f"Starting ensemble analysis for contract: {contract.get('id', 'unknown')}")
            
            # Extract features
            features = self._extract_features(contract)
            
            # Perform different types of analysis
            analyses = {}
            
            # Statistical analysis
            analyses["statistical"] = await self._statistical_analysis(contract, features)
            
            # Machine learning analysis (if available)
            if SKLEARN_AVAILABLE:
                analyses["ml"] = await self._ml_analysis(contract, features)
            
            # Time series analysis
            analyses["time_series"] = await self._time_series_analysis(contract)
            
            # Market sentiment analysis
            analyses["sentiment"] = await self._sentiment_analysis(contract)
            
            # Combine analyses
            ensemble_result = self._combine_analyses(analyses, contract)
            
            logger.info(f"Ensemble analysis completed for contract: {contract.get('id', 'unknown')}")
            return ensemble_result
            
        except Exception as e:
            logger.error(f"Ensemble analysis failed: {e}")
            return self._fallback_analysis(contract)
    
    def _extract_features(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from contract for analysis"""
        features = {}
        
        # Basic contract features
        features["contract_id"] = contract.get("id", "")
        features["title_length"] = len(contract.get("title", ""))
        features["description_length"] = len(contract.get("description", ""))
        
        # Price features
        if "current_price" in contract:
            features["current_price"] = float(contract["current_price"])
        else:
            features["current_price"] = 0.5  # Default to 50%
        
        # Time features
        if "expiration_date" in contract:
            try:
                expiration = pd.to_datetime(contract["expiration_date"])
                now = pd.Timestamp.now()
                features["days_to_expiration"] = (expiration - now).days
            except:
                features["days_to_expiration"] = 30  # Default
        
        # Volume features
        if "volume" in contract:
            features["volume"] = float(contract["volume"])
        else:
            features["volume"] = 0
        
        # Outcome features
        if "outcomes" in contract:
            features["num_outcomes"] = len(contract["outcomes"])
            features["outcomes"] = contract["outcomes"]
        else:
            features["num_outcomes"] = 2
            features["outcomes"] = ["Yes", "No"]
        
        return features
    
    async def _statistical_analysis(self, contract: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis"""
        try:
            # Basic probability estimation
            current_price = features["current_price"]
            
            # Simple statistical model based on price
            # This is a basic model - in practice, you'd use more sophisticated approaches
            probability = current_price
            confidence = 0.5 + 0.3 * (1 - abs(current_price - 0.5))  # Higher confidence near extremes
            
            # Calculate volatility estimate
            volatility = 0.1 + 0.2 * (1 - confidence)
            
            return {
                "probability": probability,
                "confidence": confidence,
                "volatility": volatility,
                "method": "statistical",
                "features_used": list(features.keys())
            }
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            return {
                "probability": 0.5,
                "confidence": 0.0,
                "volatility": 0.5,
                "method": "statistical",
                "error": str(e)
            }
    
    async def _ml_analysis(self, contract: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, Any]:
        """Perform machine learning analysis"""
        try:
            # This is a simplified ML analysis
            # In practice, you'd train models on historical data
            
            # Create feature vector
            feature_vector = np.array([
                features["current_price"],
                features["days_to_expiration"] / 365,  # Normalize to years
                features["volume"] / 1000,  # Normalize volume
                features["title_length"] / 100,  # Normalize title length
            ]).reshape(1, -1)
            
            # Scale features
            if self.scaler is not None:
                feature_vector_scaled = self.scaler.fit_transform(feature_vector)
            else:
                feature_vector_scaled = feature_vector
            
            # Get predictions from models
            predictions = {}
            for name, model in self.models.items():
                # For demonstration, use simple heuristics
                # In practice, these would be trained models
                if name == "random_forest":
                    predictions[name] = 0.5 + 0.1 * np.random.normal()
                elif name == "linear_regression":
                    predictions[name] = features["current_price"]
            
            # Ensemble prediction
            ensemble_prediction = np.mean(list(predictions.values()))
            
            return {
                "probability": float(ensemble_prediction),
                "confidence": 0.6,
                "model_predictions": predictions,
                "method": "machine_learning",
                "features_used": list(features.keys())
            }
            
        except Exception as e:
            logger.error(f"ML analysis failed: {e}")
            return {
                "probability": 0.5,
                "confidence": 0.0,
                "method": "machine_learning",
                "error": str(e)
            }
    
    async def _time_series_analysis(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Perform time series analysis"""
        try:
            # This is a simplified time series analysis
            # In practice, you'd analyze historical price movements
            
            # Simulate time series analysis
            current_price = contract.get("current_price", 0.5)
            
            # Simple trend analysis
            trend = "neutral"
            if current_price > 0.6:
                trend = "bullish"
            elif current_price < 0.4:
                trend = "bearish"
            
            # Momentum indicator
            momentum = 0.5 + 0.2 * (current_price - 0.5)
            
            return {
                "trend": trend,
                "momentum": momentum,
                "current_price": current_price,
                "method": "time_series"
            }
            
        except Exception as e:
            logger.error(f"Time series analysis failed: {e}")
            return {
                "trend": "neutral",
                "momentum": 0.5,
                "method": "time_series",
                "error": str(e)
            }
    
    async def _sentiment_analysis(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Perform market sentiment analysis"""
        try:
            # This is a simplified sentiment analysis
            # In practice, you'd analyze news, social media, etc.
            
            title = contract.get("title", "").lower()
            description = contract.get("description", "").lower()
            
            # Simple keyword-based sentiment
            positive_words = ["win", "success", "positive", "up", "gain", "profit"]
            negative_words = ["loss", "fail", "negative", "down", "decline", "risk"]
            
            positive_count = sum(1 for word in positive_words if word in title or word in description)
            negative_count = sum(1 for word in negative_words if word in title or word in description)
            
            sentiment_score = (positive_count - negative_count) / max(positive_count + negative_count, 1)
            sentiment = "neutral"
            
            if sentiment_score > 0.2:
                sentiment = "positive"
            elif sentiment_score < -0.2:
                sentiment = "negative"
            
            return {
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "positive_keywords": positive_count,
                "negative_keywords": negative_count,
                "method": "sentiment"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "method": "sentiment",
                "error": str(e)
            }
    
    def _combine_analyses(self, analyses: Dict[str, Any], contract: Dict[str, Any]) -> Dict[str, Any]:
        """Combine different analysis results"""
        try:
            # Weighted combination of different analyses
            weights = {
                "statistical": 0.3,
                "ml": 0.3,
                "time_series": 0.2,
                "sentiment": 0.2
            }
            
            combined_probability = 0.0
            total_weight = 0.0
            confidences = []
            
            for analysis_type, analysis in analyses.items():
                if analysis_type in weights and "probability" in analysis:
                    weight = weights[analysis_type]
                    combined_probability += analysis["probability"] * weight
                    total_weight += weight
                    
                    if "confidence" in analysis:
                        confidences.append(analysis["confidence"])
            
            # Normalize probability
            if total_weight > 0:
                combined_probability /= total_weight
            else:
                combined_probability = 0.5
            
            # Average confidence
            avg_confidence = np.mean(confidences) if confidences else 0.5
            
            return {
                "contract_id": contract.get("id"),
                "ensemble_probability": combined_probability,
                "ensemble_confidence": avg_confidence,
                "individual_analyses": analyses,
                "weights_used": weights,
                "timestamp": asyncio.get_event_loop().time(),
                "method": "ensemble"
            }
            
        except Exception as e:
            logger.error(f"Analysis combination failed: {e}")
            return {
                "contract_id": contract.get("id"),
                "ensemble_probability": 0.5,
                "ensemble_confidence": 0.0,
                "individual_analyses": analyses,
                "error": str(e),
                "method": "ensemble"
            }
    
    def _fallback_analysis(self, contract: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback analysis when ensemble methods fail"""
        return {
            "contract_id": contract.get("id"),
            "ensemble_probability": 0.5,
            "ensemble_confidence": 0.0,
            "individual_analyses": {
                "statistical": {"probability": 0.5, "confidence": 0.0, "method": "fallback"},
                "time_series": {"trend": "neutral", "method": "fallback"},
                "sentiment": {"sentiment": "neutral", "method": "fallback"}
            },
            "error": "Ensemble analysis failed",
            "method": "fallback"
        }