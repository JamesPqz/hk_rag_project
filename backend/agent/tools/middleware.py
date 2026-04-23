import time
from typing import Optional

from backend.utils.logger_handler import logger
from backend.utils.prompts_loader import load_report_prompt, load_rag_summarize_prompt, load_react_system_prompt, \
    load_sys_prompt


class LogMiddleware:
    """日志中间件：记录请求和响应"""

    def before(self, query: str) -> str:
        logger.info(f"Agent request: {query[:100]}...")
        return query

    def after(self, response: str) -> str:
        logger.info(f"Agent response: {response[:100]}...")
        return response


class TimerMiddleware:
    """计时中间件：记录执行时间"""

    def __init__(self):
        self.start_time = None

    def before(self, query: str) -> str:
        self.start_time = time.time()
        return query

    def after(self, response: str) -> str:
        elapsed = time.time() - self.start_time
        logger.info(f"Agent execution time: {elapsed:.2f}s")
        return response


class PromptSwitchMiddleware:
    """提示词切换中间件：根据上下文动态选择提示词"""

    def __init__(self):
        self.current_prompt = None

    def before(self, query: str, context: Optional[dict] = None) -> tuple[str, str]:

        context = context or {}

        # 1. 报告生成场景
        if context.get('report') or self._is_report_request(query):
            prompt_name = "report_prompt"
            prompt_content = load_report_prompt()
            logger.info(f"Switch to {prompt_name}")
            return prompt_name, prompt_content

        # 2. 文档总结场景
        if context.get('summarize') or self._is_summary_request(query):
            prompt_name = "rag_summarize"
            prompt_content = load_rag_summarize_prompt()
            logger.info(f"Switch to {prompt_name}")
            return prompt_name, prompt_content

        # 3. ReAct Agent 场景（需要工具调用）
        if context.get('react_mode') or self._is_react_request(query):
            prompt_name = "react_system"
            prompt_content = load_react_system_prompt()
            logger.info(f"Switch to {prompt_name}")
            return prompt_name, prompt_content

        # 4. 默认问答场景
        prompt_name = "main_prompt"
        prompt_content = load_sys_prompt()
        return prompt_name, prompt_content

    def _is_report_request(self, query: str) -> bool:
        keywords = ["报告", "生成报告", "写报告", "输出报告", "总结报告"]
        return any(kw in query for kw in keywords)

    def _is_summary_request(self, query: str) -> bool:
        keywords = ["总结", "摘要", "概括", "归纳", "提炼"]
        return any(kw in query for kw in keywords)

    def _is_react_request(self, query: str) -> bool:
        keywords = ["计算", "查", "多少", "几点", "天气", "股票", "翻译", "新闻", "发邮件"]
        return any(kw in query for kw in keywords)