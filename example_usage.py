"""
Example Usage of Kalshi AI Hedge Fund Framework

This script demonstrates how to use the framework to analyze contracts
and generate trading signals.
"""

import asyncio
import json
from kalshi_hedge_fund import KalshiHedgeFund


async def main():
    """Example usage of the framework"""
    
    # Initialize the framework
    # Note: You need to create a config.py file with your API keys
    try:
        hedge_fund = KalshiHedgeFund(config_path="config.py")
    except Exception as e:
        print(f"Failed to initialize framework: {e}")
        print("Please ensure you have created a config.py file with your API keys")
        return
    
    try:
        # Example 1: Analyze a single contract
        print("=== Example 1: Analyzing a single contract ===")
        
        # Replace with an actual contract ID from Kalshi
        contract_id = "EXAMPLE-CONTRACT-ID"
        
        try:
            # Get contract information
            contract = await hedge_fund.get_contract(contract_id)
            print(f"Retrieved contract: {contract.get('title', 'Unknown')}")
            
            # Analyze the contract
            analysis = await hedge_fund.analyze_contract(contract)
            print(f"Analysis completed with confidence: {analysis.get('statistical_analysis', {}).get('ensemble_confidence', 0):.2f}")
            
            # Generate trading signal
            signal = await hedge_fund.generate_signal(analysis)
            print(f"Generated signal: {signal.get('action', 'UNKNOWN')} with confidence {signal.get('confidence', 0):.2f}")
            
            # Save results
            results = {
                "contract": contract,
                "analysis": analysis,
                "signal": signal
            }
            
            with open("example_analysis.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            print("Results saved to example_analysis.json")
            
        except Exception as e:
            print(f"Error analyzing contract: {e}")
        
        # Example 2: Get portfolio status
        print("\n=== Example 2: Getting portfolio status ===")
        
        try:
            portfolio_status = await hedge_fund.get_portfolio_status()
            print(f"Portfolio value: ${portfolio_status.get('portfolio', {}).get('total_value', 0):,.2f}")
            print(f"Number of positions: {portfolio_status.get('portfolio', {}).get('positions', [])}")
            
            # Save portfolio status
            with open("portfolio_status.json", "w") as f:
                json.dump(portfolio_status, f, indent=2, default=str)
            print("Portfolio status saved to portfolio_status.json")
            
        except Exception as e:
            print(f"Error getting portfolio status: {e}")
        
        # Example 3: Search for contracts
        print("\n=== Example 3: Searching for contracts ===")
        
        try:
            # Search for contracts related to elections
            contracts = await hedge_fund.kalshi_collector.search_contracts("election", limit=5)
            print(f"Found {len(contracts)} contracts related to elections")
            
            for i, contract in enumerate(contracts[:3], 1):
                print(f"{i}. {contract.get('title', 'Unknown')} (ID: {contract.get('id', 'Unknown')})")
            
            # Save search results
            search_results = {
                "query": "election",
                "contracts": contracts,
                "count": len(contracts)
            }
            
            with open("search_results.json", "w") as f:
                json.dump(search_results, f, indent=2, default=str)
            print("Search results saved to search_results.json")
            
        except Exception as e:
            print(f"Error searching contracts: {e}")
        
        # Example 4: Run strategy on multiple contracts
        print("\n=== Example 4: Running strategy on multiple contracts ===")
        
        try:
            # Get some active contracts
            active_contracts = await hedge_fund.kalshi_collector.get_active_contracts()
            
            if active_contracts:
                # Take first 3 contracts for demonstration
                contract_ids = [contract.get('id') for contract in active_contracts[:3] if contract.get('id')]
                
                print(f"Running strategy on {len(contract_ids)} contracts...")
                strategy_results = await hedge_fund.run_strategy(contract_ids)
                
                print(f"Strategy completed. Processed {strategy_results.get('total_contracts', 0)} contracts")
                
                # Count signals by action
                signals = {}
                for result in strategy_results.get('results', []):
                    action = result.get('signal', {}).get('action', 'UNKNOWN')
                    signals[action] = signals.get(action, 0) + 1
                
                print("Signal distribution:")
                for action, count in signals.items():
                    print(f"  {action}: {count}")
                
                # Save strategy results
                with open("strategy_results.json", "w") as f:
                    json.dump(strategy_results, f, indent=2, default=str)
                print("Strategy results saved to strategy_results.json")
            else:
                print("No active contracts found")
                
        except Exception as e:
            print(f"Error running strategy: {e}")
    
    finally:
        # Cleanup
        await hedge_fund.shutdown()
        print("\nFramework shutdown completed")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())