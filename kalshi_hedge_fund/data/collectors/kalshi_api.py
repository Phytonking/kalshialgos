"""
Kalshi API Data Collector

This module handles all interactions with the Kalshi trading API to collect
market data, contract information, and trading data.
"""

import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class KalshiAPICollector:
    """
    Collector for Kalshi API data
    
    Handles authentication, rate limiting, and data collection from the Kalshi
    trading platform API.
    """
    
    def __init__(self, config):
        """
        Initialize the Kalshi API collector
        
        Args:
            config: Configuration object containing API credentials
        """
        self.config = config
        self.base_url = config.kalshi_base_url
        self.api_key = config.kalshi_api_key
        self.api_secret = config.kalshi_api_secret
        
        # Session for HTTP requests
        self.session = None
        
        # Rate limiting
        self.request_count = 0
        self.last_request_time = None
        self.rate_limit_delay = 0.1  # 100ms between requests
        
        logger.info("Kalshi API Collector initialized")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
            )
        return self.session
    
    async def _rate_limit(self):
        """Implement rate limiting"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < self.rate_limit_delay:
                await asyncio.sleep(self.rate_limit_delay - elapsed)
        
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make authenticated request to Kalshi API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            API response data
        """
        await self._rate_limit()
        
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                data = await response.json()
                
                logger.debug(f"API request successful: {method} {endpoint}")
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {method} {endpoint} - {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            raise
    
    async def get_contract(self, contract_id: str) -> Dict[str, Any]:
        """
        Get contract information
        
        Args:
            contract_id: The Kalshi contract ID
            
        Returns:
            Contract information dictionary
        """
        endpoint = f"/contracts/{contract_id}"
        return await self._make_request("GET", endpoint)
    
    async def get_contracts(self, series_id: Optional[str] = None, 
                          limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of contracts
        
        Args:
            series_id: Optional series ID to filter by
            limit: Maximum number of contracts to return
            
        Returns:
            List of contract dictionaries
        """
        params: Dict[str, Any] = {"limit": limit}
        if series_id:
            params["series_id"] = series_id
        
        endpoint = "/contracts"
        response = await self._make_request("GET", endpoint, params=params)
        return response.get("contracts", [])
    
    async def get_market_history(self, contract_id: str, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get market history for a contract
        
        Args:
            contract_id: The Kalshi contract ID
            start_time: Start time for history
            end_time: End time for history
            
        Returns:
            List of market history entries
        """
        params = {}
        if start_time:
            params["start_time"] = start_time.isoformat()
        if end_time:
            params["end_time"] = end_time.isoformat()
        
        endpoint = f"/contracts/{contract_id}/history"
        response = await self._make_request("GET", endpoint, params=params)
        return response.get("history", [])
    
    async def get_order_book(self, contract_id: str) -> Dict[str, Any]:
        """
        Get order book for a contract
        
        Args:
            contract_id: The Kalshi contract ID
            
        Returns:
            Order book data
        """
        endpoint = f"/contracts/{contract_id}/book"
        return await self._make_request("GET", endpoint)
    
    async def get_user_positions(self) -> List[Dict[str, Any]]:
        """
        Get current user positions
        
        Returns:
            List of position dictionaries
        """
        endpoint = "/positions"
        response = await self._make_request("GET", endpoint)
        return response.get("positions", [])
    
    async def get_user_orders(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user orders
        
        Args:
            status: Optional order status filter
            
        Returns:
            List of order dictionaries
        """
        params = {}
        if status:
            params["status"] = status
        
        endpoint = "/orders"
        response = await self._make_request("GET", endpoint, params=params)
        return response.get("orders", [])
    
    async def get_user_balance(self) -> Dict[str, Any]:
        """
        Get user account balance
        
        Returns:
            Balance information
        """
        endpoint = "/user/balance"
        return await self._make_request("GET", endpoint)
    
    async def get_series(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get list of series
        
        Args:
            limit: Maximum number of series to return
            
        Returns:
            List of series dictionaries
        """
        endpoint = "/series"
        response = await self._make_request("GET", endpoint, params={"limit": limit})
        return response.get("series", [])
    
    async def get_series_contracts(self, series_id: str) -> List[Dict[str, Any]]:
        """
        Get all contracts in a series
        
        Args:
            series_id: The series ID
            
        Returns:
            List of contract dictionaries
        """
        return await self.get_contracts(series_id=series_id)
    
    async def search_contracts(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for contracts by title or description
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching contracts
        """
        # Note: This is a simplified search implementation
        # In practice, you might need to implement this differently
        # based on the actual Kalshi API capabilities
        
        all_contracts = await self.get_contracts(limit=1000)
        matching_contracts = []
        
        query_lower = query.lower()
        for contract in all_contracts:
            title = contract.get("title", "").lower()
            description = contract.get("description", "").lower()
            
            if query_lower in title or query_lower in description:
                matching_contracts.append(contract)
                
                if len(matching_contracts) >= limit:
                    break
        
        return matching_contracts
    
    async def get_active_contracts(self) -> List[Dict[str, Any]]:
        """
        Get all active contracts
        
        Returns:
            List of active contract dictionaries
        """
        all_contracts = await self.get_contracts(limit=1000)
        active_contracts = []
        
        for contract in all_contracts:
            status = contract.get("status", "")
            if status.lower() == "active":
                active_contracts.append(contract)
        
        return active_contracts
    
    async def close(self):
        """Close the HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("Kalshi API Collector session closed")