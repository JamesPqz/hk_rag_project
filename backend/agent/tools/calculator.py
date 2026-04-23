from backend.agent.tools.tools_base import ToolsRegistry


def _calculate(expression:str)-> str:
    """计算数学表达式，如 '100*50/2' 或 '(10+5)*3'"""
    all_allows = set("0123456789+-*/(). ")
    if not all(c in all_allows for c in expression):
        return "error: expression contains illegal chars"

    try:
        result = eval(expression)
        return str(result)
    except ZeroDivisionError:
        return "error: 0 division"
    except Exception as e:
        return f"calculate error: {str(e)}"

ToolsRegistry.register(
    name="calculator",
    description="计算数学表达式，如 '100*50/2' 或 '(10+5)*3'",
    func=_calculate
)