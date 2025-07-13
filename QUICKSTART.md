# Quick Start Guide

This guide will help you get the Kalshi AI Hedge Fund Framework up and running quickly.

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for full deployment)
- Kalshi API credentials
- OpenAI API key (optional, for LLM features)

## Installation

### Option 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/kalshi-hedge-fund.git
   cd kalshi-hedge-fund
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Create configuration file**
   ```bash
   cp config_example.py config.py
   # Edit config.py with your API keys
   ```

### Option 2: Docker Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/kalshi-hedge-fund.git
   cd kalshi-hedge-fund
   ```

2. **Set up environment variables**
   ```bash
   export KALSHI_API_KEY="your_kalshi_api_key"
   export KALSHI_API_SECRET="your_kalshi_api_secret"
   export OPENAI_API_KEY="your_openai_api_key"
   ```

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

## Configuration

1. **Copy the example configuration**
   ```bash
   cp config_example.py config.py
   ```

2. **Edit `config.py` with your credentials**
   ```python
   # Required: Kalshi API credentials
   KALSHI_API_KEY = "your_actual_kalshi_api_key"
   KALSHI_API_SECRET = "your_actual_kalshi_api_secret"
   
   # Required: Database connection
   DATABASE_URL = "postgresql://user:password@localhost/kalshi_db"
   
   # Optional: OpenAI API for LLM features
   OPENAI_API_KEY = "your_openai_api_key"
   ```

## Quick Test

1. **Run the example script**
   ```bash
   python example_usage.py
   ```

2. **Or use the CLI**
   ```bash
   # Analyze a contract
   python -m kalshi_hedge_fund.cli analyze --contract-id "CONTRACT-ID"
   
   # Get portfolio status
   python -m kalshi_hedge_fund.cli portfolio-status
   
   # Search for contracts
   python -m kalshi_hedge_fund.cli search-contracts --query "election"
   ```

## Basic Usage

### Python API

```python
import asyncio
from kalshi_hedge_fund import KalshiHedgeFund

async def main():
    # Initialize the framework
    hedge_fund = KalshiHedgeFund(config_path="config.py")
    
    # Get a contract
    contract = await hedge_fund.get_contract("CONTRACT-ID")
    
    # Analyze the contract
    analysis = await hedge_fund.analyze_contract(contract)
    
    # Generate trading signal
    signal = await hedge_fund.generate_signal(analysis)
    
    # Execute trade (if signal is strong enough)
    if signal.get("confidence", 0) > 0.7:
        result = await hedge_fund.execute_trade(signal)
    
    # Cleanup
    await hedge_fund.shutdown()

# Run the example
asyncio.run(main())
```

### Command Line Interface

```bash
# Analyze a single contract
kalshi-hedge-fund analyze --contract-id "CONTRACT-ID" --output results.json

# Run strategy on multiple contracts
kalshi-hedge-fund run-strategy --contracts "CONTRACT1,CONTRACT2,CONTRACT3" --output strategy.json

# Get portfolio status
kalshi-hedge-fund portfolio-status --output portfolio.json

# Search for contracts
kalshi-hedge-fund search-contracts --query "election" --limit 10 --output search.json
```

## Monitoring

If using Docker Compose, you can access:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Framework API**: http://localhost:8000

## Next Steps

1. **Review the documentation** in the README.md
2. **Explore the example scripts** in the examples/ directory
3. **Customize the configuration** for your trading strategy
4. **Set up monitoring** and alerts
5. **Test with small amounts** before deploying with real capital

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure your Kalshi API credentials are correct
   - Check that your API keys have the necessary permissions

2. **Database Connection Issues**
   - Verify your PostgreSQL connection string
   - Ensure the database is running and accessible

3. **LLM Features Not Working**
   - Check your OpenAI API key
   - Ensure you have sufficient API credits

4. **Docker Issues**
   - Make sure Docker and Docker Compose are installed
   - Check that ports 5432, 6379, 8000, 9090, and 3000 are available

### Getting Help

- Check the logs: `docker-compose logs kalshi-hedge-fund`
- Review the error messages in the console output
- Check the framework logs in the `logs/` directory

## Security Notes

- Never commit your `config.py` file with real API keys
- Use environment variables for sensitive data in production
- Regularly rotate your API keys
- Monitor your API usage and costs

## Disclaimer

This framework is for educational and research purposes. Trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.