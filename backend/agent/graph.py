from typing import Optional, Tuple, Callable, Any

from backend.agent.react_agent import ReactAgent
from backend.agent.tools import ToolsRegistry, get_all_tools
from backend.agent.tools.middleware import  PromptSwitchMiddleware, \
    LogMiddleware, TimerMiddleware
from backend.api.chat import llm_service
from backend.models.factory import chat_model
from backend.services.intent import classify_intent
from backend.utils.logger_handler import logger
from backend.utils.prompts_loader import load_react_system_prompt, load_boundaries


def load_react_prompt() -> str:
    template = load_react_system_prompt();
    tools_desc = '\n'.join([f"- {tool.name} : {tool.description}" for tool in ToolsRegistry.get_all_tools()])
    boundaries = load_boundaries()
    return template.format(available_tools=tools_desc, boundaries=boundaries)

def create_agent():
    llm = chat_model
    tools = get_all_tools()
    middleware = [
        PromptSwitchMiddleware(),
        LogMiddleware(),
        TimerMiddleware()
    ]
    agent = ReactAgent(
        model=llm,
        tools=tools,
        middleware=middleware,
        max_iterations=10
    )

    return agent

_agent = None

def get_agent() -> ReactAgent:
    global _agent
    if _agent is None:
        _agent = create_agent()
    return _agent

def run_agent(query:str,session_id: str, context: Optional[dict] = None, is_stream:bool = False) -> Tuple[Any, list]:
    intent = classify_intent(query)

    if intent == 'CHAT':
        logger.info(f"intent:{intent}, llm response.")
        return llm_service.generate(query)

    logger.info(f"intent:{intent}, run react agent.")

    agent = get_agent()
    if is_stream:
        generator = agent.execute_stream(query,session_id, context)
        sources = agent.context.get('sources') or []
        return generator, sources
    else:
        answer = agent.run(query,session_id, context)
        if not answer:
            return llm_service.generate(f"知识库中没有相关信息，请用自己的知识回答：{query}")
        sources = agent.context.get('sources') or []

        return answer, sources