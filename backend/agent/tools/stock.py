from backend.agent.tools.tools_base import ToolsRegistry

def _get_stock_price(symbol: str) -> str:
    """查询股票实时价格，如 'APPLE'（苹果）、'00700.HK'（腾讯）"""
    try:
        import yfinance as yf
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")['Close'].iloc[-1]
        return f"{symbol} price: ${price:.2f}"
    except ImportError:
        return "need to install yfinance: pip install yfinance"
    except Exception as e:
        return f"get price fail: {e}"

ToolsRegistry.register(
    name="stock",
    description="查询股票实时价格，如 'AAPL'（苹果）、'00700.HK'（腾讯）",
    func=_get_stock_price
)