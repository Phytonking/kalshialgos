"""
Command Line Interface for Kalshi AI Hedge Fund Framework

This module provides a CLI for interacting with the framework,
including running strategies, analyzing contracts, and monitoring performance.
"""

import asyncio
import click
import json
from typing import List, Optional
from pathlib import Path

from .core import KalshiHedgeFund
from .config import Config


@click.group()
@click.version_option()
def cli():
    """Kalshi AI Hedge Fund Framework CLI"""
    pass


@cli.command()
@click.option('--config', '-c', 'config_path', help='Path to configuration file')
@click.option('--contract-id', '-i', help='Contract ID to analyze')
@click.option('--output', '-o', help='Output file for results (JSON)')
def analyze(config_path: Optional[str], contract_id: Optional[str], output: Optional[str]):
    """Analyze a single contract"""
    asyncio.run(_analyze_contract(config_path, contract_id, output))


@cli.command()
@click.option('--config', '-c', 'config_path', help='Path to configuration file')
@click.option('--contracts', '-i', help='Comma-separated list of contract IDs')
@click.option('--output', '-o', help='Output file for results (JSON)')
def run_strategy(config_path: Optional[str], contracts: Optional[str], output: Optional[str]):
    """Run the complete strategy on multiple contracts"""
    if contracts:
        contract_ids = [cid.strip() for cid in contracts.split(',')]
    else:
        contract_ids = []
    
    asyncio.run(_run_strategy(config_path, contract_ids, output))


@cli.command()
@click.option('--config', '-c', 'config_path', help='Path to configuration file')
@click.option('--output', '-o', help='Output file for results (JSON)')
def portfolio_status(config_path: Optional[str], output: Optional[str]):
    """Get current portfolio status and risk metrics"""
    asyncio.run(_get_portfolio_status(config_path, output))


@cli.command()
@click.option('--config', '-c', 'config_path', help='Path to configuration file')
@click.option('--query', '-q', help='Search query for contracts')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
@click.option('--output', '-o', help='Output file for results (JSON)')
def search_contracts(config_path: Optional[str], query: str, limit: int, output: Optional[str]):
    """Search for contracts"""
    asyncio.run(_search_contracts(config_path, query, limit, output))


async def _analyze_contract(config_path: Optional[str], contract_id: Optional[str], output: Optional[str]):
    """Analyze a single contract"""
    try:
        # Initialize framework
        hedge_fund = KalshiHedgeFund(config_path=config_path)
        
        if not contract_id:
            click.echo("Error: Contract ID is required")
            return
        
        click.echo(f"Analyzing contract: {contract_id}")
        
        # Get contract
        contract = await hedge_fund.get_contract(contract_id)
        
        # Analyze contract
        analysis = await hedge_fund.analyze_contract(contract)
        
        # Generate signal
        signal = await hedge_fund.generate_signal(analysis)
        
        # Prepare results
        results = {
            "contract": contract,
            "analysis": analysis,
            "signal": signal,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Results saved to: {output}")
        else:
            click.echo(json.dumps(results, indent=2, default=str))
        
        # Cleanup
        await hedge_fund.shutdown()
        
    except Exception as e:
        click.echo(f"Error: {e}")
        return 1


async def _run_strategy(config_path: Optional[str], contract_ids: List[str], output: Optional[str]):
    """Run strategy on multiple contracts"""
    try:
        # Initialize framework
        hedge_fund = KalshiHedgeFund(config_path=config_path)
        
        if not contract_ids:
            click.echo("Error: At least one contract ID is required")
            return
        
        click.echo(f"Running strategy on {len(contract_ids)} contracts")
        
        # Run strategy
        results = await hedge_fund.run_strategy(contract_ids)
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Results saved to: {output}")
        else:
            click.echo(json.dumps(results, indent=2, default=str))
        
        # Cleanup
        await hedge_fund.shutdown()
        
    except Exception as e:
        click.echo(f"Error: {e}")
        return 1


async def _get_portfolio_status(config_path: Optional[str], output: Optional[str]):
    """Get portfolio status"""
    try:
        # Initialize framework
        hedge_fund = KalshiHedgeFund(config_path=config_path)
        
        click.echo("Getting portfolio status...")
        
        # Get portfolio status
        status = await hedge_fund.get_portfolio_status()
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(status, f, indent=2, default=str)
            click.echo(f"Portfolio status saved to: {output}")
        else:
            click.echo(json.dumps(status, indent=2, default=str))
        
        # Cleanup
        await hedge_fund.shutdown()
        
    except Exception as e:
        click.echo(f"Error: {e}")
        return 1


async def _search_contracts(config_path: Optional[str], query: str, limit: int, output: Optional[str]):
    """Search for contracts"""
    try:
        # Initialize framework
        hedge_fund = KalshiHedgeFund(config_path=config_path)
        
        if not query:
            click.echo("Error: Search query is required")
            return
        
        click.echo(f"Searching for contracts: {query}")
        
        # Search contracts
        contracts = await hedge_fund.kalshi_collector.search_contracts(query, limit)
        
        # Prepare results
        results = {
            "query": query,
            "limit": limit,
            "contracts": contracts,
            "count": len(contracts),
            "timestamp": asyncio.get_event_loop().time()
        }
        
        # Output results
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            click.echo(f"Search results saved to: {output}")
        else:
            click.echo(json.dumps(results, indent=2, default=str))
        
        # Cleanup
        await hedge_fund.shutdown()
        
    except Exception as e:
        click.echo(f"Error: {e}")
        return 1


def main():
    """Main CLI entry point"""
    cli()


if __name__ == "__main__":
    main()