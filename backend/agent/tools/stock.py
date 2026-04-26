from backend.agent.tools.tools_base import ToolsRegistry

def _get_stock_price(symbol: str) -> str:
    """查询股票实时价格，如 'APPLE'（苹果）、'00700.HK'（腾讯）"""
    try:
        import yfinance as yf
        if symbol.isdigit() or (symbol.startswith('0') and len(symbol) == 5):
            symbol = symbol.lstrip('0') + '.HK'

        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]

        info = stock.info
        name = info.get('longName', symbol)

        return f"{name} 最新价格: ${price:.2f} HKD"
    except ImportError:
        return "need to install yfinance: pip install yfinance"
    except Exception as e:
        return f"get price fail: {e}"

ToolsRegistry.register(
    name="get_stock_price",
    description="查询股票实时价格，如 'AAPL'（苹果）、'00700.HK'（腾讯）",
    func=_get_stock_price
)