"""
Kalshi AI Hedge Fund Framework

An open source framework for automated hedge fund operations focused on Kalshi event contracts,
leveraging LLM reasoning, deep research capabilities, and statistical analysis for systematic trading.
"""

__version__ = "0.1.0"
__author__ = "Kalshi AI Hedge Fund Team"
__email__ = "team@kalshi-hedge-fund.com"

from .core import KalshiHedgeFund
from .config import Config

__all__ = [
    "KalshiHedgeFund",
    "Config",
    "__version__",
    "__author__",
    "__email__",
]