"""
Example Configuration File for Kalshi AI Hedge Fund Framework

Copy this file to config.py and update with your actual API keys and settings.
"""

# Kalshi API Configuration
KALSHI_API_KEY = "your_kalshi_api_key_here"
KALSHI_API_SECRET = "your_kalshi_api_secret_here"
KALSHI_BASE_URL = "https://trading-api.kalshi.com"

# Database Configuration
DATABASE_URL = "postgresql://user:password@localhost/kalshi_db"
REDIS_URL = "redis://localhost:6379"

# LLM Configuration
LLM_MODEL = "gpt-4"
OPENAI_API_KEY = "your_openai_api_key_here"
OPENAI_ORGANIZATION = "your_openai_org_id_here"  # Optional

# Risk Management Configuration
MAX_POSITION_SIZE = 0.05  # 5% of portfolio
MAX_DRAWDOWN = 0.20  # 20% maximum drawdown
VAR_LIMIT = 0.02  # 2% daily VaR
MAX_CORRELATION = 0.7  # Maximum correlation between positions

# Trading Configuration
MIN_CONFIDENCE_THRESHOLD = 0.7
MAX_SLIPPAGE = 0.01  # 1% maximum slippage
ORDER_TIMEOUT = 30  # 30 seconds

# Data Collection Configuration (Optional)
NEWS_API_KEY = "your_news_api_key_here"  # Optional
TWITTER_BEARER_TOKEN = "your_twitter_token_here"  # Optional
ALPHA_VANTAGE_KEY = "your_alpha_vantage_key_here"  # Optional

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "kalshi_hedge_fund.log"

# Monitoring Configuration
PROMETHEUS_PORT = 8000
HEALTH_CHECK_INTERVAL = 60  # seconds

# Backtesting Configuration
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2024-01-01"
INITIAL_CAPITAL = 1000000  # $1M

# Model Configuration
MODEL_UPDATE_FREQUENCY = 3600  # 1 hour
FEATURE_WINDOW_SIZE = 30  # 30 days
PREDICTION_HORIZON = 7  # 7 days