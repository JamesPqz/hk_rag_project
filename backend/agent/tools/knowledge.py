from typing import Dict, Any

from backend.agent.tools.tools_base import ToolsRegistry
from backend.services.retrieval_service import RetrievalService
from backend.utils.logger_handler import logger

def _search_knowledge(query:str)-> Dict[str, Any]:
    """搜索知识库，用于查询文档中的信息。输入：问题"""
    try:
        result = RetrievalService.retrieve_with_citation(query, k=4)
        return result
    except Exception as e:
        logger.info(f"search knowledge error:{str(e)}")
        return {}

ToolsRegistry.register(
    name='knowledge',
    description='搜索知识库，用于查询文档中的信息。输入：问题',
    func=_search_knowledge
)