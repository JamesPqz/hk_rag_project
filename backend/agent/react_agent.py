import json
from time import sleep
from typing import List, Optional, Any, Dict

from instructor.providers.anthropic.utils import SystemMessage
from langchain_openai import ChatOpenAI

from backend.api.chat import llm_service
from backend.services.conversation_service import ConversationService
from backend.services.query_cache import QueryCache
from backend.utils.logger_handler import logger
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from backend.utils.prompts_loader import load_sys_prompt, load_report_prompt, load_react_system_prompt, \
    load_rag_summarize_prompt


class ReactAgent:
    def __init__(self,
                 model: ChatOpenAI,
                 tools: List[Any],
                 middleware: Optional[List[Any]],
                 max_iterations: int = 10):
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.middleware = middleware
        self.max_iterations = max_iterations
        self.context = {}

    def _execute_tool(self, tool_name: str, tool_input: Dict) -> str:
        tool = self.tools.get(tool_name)
        if not tool:
            return f"can't find tool:{tool_name}"
        try:
            result = tool.invoke(tool_input)
            if isinstance(result, Dict) and result['sources']:
                self.context['sources'] = result['sources']
                return result['context']
            return str(result)
        except Exception as e:
            logger.info(f"execute tool error:{str(e)}")
            return f"execute tool fail:{str(e)}"

    def _run_middleware_before(self, query: str) -> tuple[str, str]:
        prompt_name = "main_prompt"
        prompt_content = None

        for m in self.middleware:
            if hasattr(m, 'before'):
                query = m.before(query)
                if isinstance(query, tuple):
                    prompt_name, prompt_content = query

        return prompt_name, prompt_content

    def _run_middleware_after(self, response: str) -> str:
        for m in self.middleware:
            if hasattr(m, 'after'):
                response = m.after(response)

        return response

    def _get_prompt_by_name(self, prompt_name: str) -> str:
        if prompt_name == "report_prompt":
            return load_report_prompt()
        elif prompt_name == "rag_summarize":
            return load_rag_summarize_prompt()
        elif prompt_name == "react_system":
            return load_react_system_prompt()
        else:
            return load_sys_prompt()

    def run(self, query: str, session_id: str = 'default', context: Optional[dict] = None):
        if context is None:
            context = {}

        self.context = context

        prompt_name, prompt_content = self._run_middleware_before(query)
        system_prompt = prompt_content or self._get_prompt_by_name(prompt_name)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        model_with_tools = self.model.bind_tools(list(self.tools.values()))
        all_used_tools = []

        resp = ""
        for i in range(self.max_iterations):
            resp = model_with_tools.invoke(messages)
            messages.append(resp)

            if not resp.tool_calls:
                break

            all_used_tools.append(json.dumps(resp.tool_calls))
            for tool_call in resp.tool_calls:
                tool_name = tool_call['name']
                tool_input = tool_call['args']

                logger.info(f"call tool:{tool_name}, input: {tool_input}")
                result = self._execute_tool(tool_name, tool_input)
                logger.info(f"tool result:{result}")

                messages.append(ToolMessage(content=result, tool_call_id=tool_call['id']))

        answer = self._run_middleware_after(resp.content)
        return answer, all_used_tools

    def execute_stream(self, query: str, session_id: str = 'default', context: Optional[dict] = None):
        if context is None:
            context = {}

        self.context = context

        prompt_name, prompt_content = self._run_middleware_before(query)
        system_prompt = prompt_content or self._get_prompt_by_name(prompt_name)

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        model_with_tools = self.model.bind_tools(list(self.tools.values()))
        conv_service = ConversationService(session_id)

        all_used_tools = []

        for i in range(self.max_iterations):
            resp = model_with_tools.invoke(messages)
            messages.append(resp)
            print(f"[interation {i}] tools:{resp.tool_calls}")

            if not resp.tool_calls:
                break

            all_used_tools.append(json.dumps(resp.tool_calls))
            for tool_call in resp.tool_calls:
                tool_name = tool_call['name']
                tool_input = tool_call['args']

                logger.info(f"call tool:{tool_name}, input: {tool_input}")
                result = self._execute_tool(tool_name, tool_input)
                logger.info(f"tool result:{result[:30]}...")

                messages.append(ToolMessage(content=result, tool_call_id=tool_call['id']))

        logger.info("工具调用完成，开始生成最终回答...")
        # logger.info(f"当前 messages: {messages}")

        async def generate():
            final_text = self._run_middleware_after(resp.content)

            summarize_template = load_rag_summarize_prompt()

            final_prompt = summarize_template.format(
                input=query,
                context=final_text
            )
            final_messages = [
                SystemMessage(content=final_prompt),
                HumanMessage(content=query)
            ]

            full_answer = ""
            async for chunk in self.model.astream(final_messages):
                if chunk.content:
                    full_answer += chunk.content
                    yield chunk.content.encode('utf-8')

            conv_service.add_message("user", query)
            conv_service.add_message("assistant", full_answer)
            QueryCache.set(query, answer=full_answer, sources=self.context.get('sources', []))

        return generate(), all_used_tools

# if __name__ == '__main__':
#     agent = ReactAgent()
#     for chunk in agent.execute_stream("what's the weather like tomorrow"):
#         print(chunk, end='', flush=True)
