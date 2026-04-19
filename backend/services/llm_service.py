import os

from langchain_openai import ChatOpenAI

from backend.utils.config_handler import rag_config


class LLM_Service:
    def __init__(self):
        self.llm = ChatOpenAI(
            model = rag_config['chat_model'],
            temperature= rag_config['temperature'],
            base_url=rag_config['base_url'],
            api_key=os.getenv(rag_config['api_key'])
        )

    def generate(self,prompt:str):
        response = self.llm.invoke(prompt)
        return response.content

    async def stream(self, prompt: str):
        async for chunk in self.llm.astream(prompt):
            yield chunk.content