
from backend.agent.tools.tools_base import ToolsRegistry

from . import knowledge
from . import time
from . import calculator
from . import stock
from . import translate
from . import weather
from . import news

__all__ = ['ToolsRegistry', 'get_all_tools']

def get_all_tools():
    return ToolsRegistry.get_all_tools()