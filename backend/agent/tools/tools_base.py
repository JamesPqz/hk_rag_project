from typing import Dict, Callable
from backend.utils.logger_handler import logger

from langchain_core.tools import tool


class ToolsRegistry:
    _tools: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, description: str, func: Callable):
        cls._tools[name] = tool(func)
        cls._tools[name].name = name
        cls._tools[name].description = description
        logger.info(f"register tool:{name}")

    @classmethod
    def get_all_tools(cls):
        return list(cls._tools.values())

    @classmethod
    def get_tool_names(cls):
        return list(cls._tools.keys())
