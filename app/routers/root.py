from openbb_terminal.sdk import openbb



def test():
   P = openbb.portfolio.load(
        transactions_file_path = '/Users/kopiko/Downloads/Openbb_SDK_API_bridge/openbbuserdata/portfolio/holdings/holdings_example.xlsx',
  benchmark_symbol = 'VTI',
  full_shares = False,
  risk_free_rate = 3.0  
    )
   return P