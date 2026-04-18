from typing import List, Tuple

from langchain_core.documents import Document
from backend.models.factory import chat_model
from backend.utils.prompts_loader import load_sys_prompt

class AnswerGenerator:
    def __init__(self):
        self.model = chat_model

    def generate(self, query:str, docs:List[Tuple[Document,float]]) -> str:
        if not docs:
            prompt = f"""用户问题：{query}

请回答上述问题。如果你不知道答案，请明确告知"我无法回答这个问题"，不要编造信息。"""
        else:
            prompts = load_sys_prompt()

if __name__ == '__main__':
    pass