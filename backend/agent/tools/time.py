from backend.agent.tools.tools_base import ToolsRegistry
from datetime import datetime


def _get_current_time()-> str:
    """获取当前日期和时间，不需要参数"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

ToolsRegistry.register(
    name='time',
    description="获取当前日期和时间，不需要参数",
    func=_get_current_time
)