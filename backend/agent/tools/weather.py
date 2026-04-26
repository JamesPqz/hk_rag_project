from backend.agent.tools.tools_base import ToolsRegistry
import requests

def _get_weather(city: str) -> str:
    """查询城市天气，如 '香港'、'深圳'、'London'"""
    try:
        url = f"https://wttr.in/{city}?format=%C+%t+%w"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return f"{city} weather：{response.text.strip()}"
        return f"get {city} weather fail"
    except requests.RequestException as e:
        return f"get weather error：{e}"
    except Exception as e:
        return f"unknown error：{e}"

ToolsRegistry.register(
    name="get_weather",
    description="查询城市天气，如 '香港'、'深圳'、'London'",
    func=_get_weather
)