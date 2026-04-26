from typing import Dict, Any

from backend.agent.tools.tools_base import ToolsRegistry
from backend.services.retrieval_service import RetrievalService
from backend.utils.config_handler import chroma_config
from backend.utils.logger_handler import logger

def _search_knowledge(query:str)-> Dict[str, Any]:
    """搜索知识库，用于查询文档中的信息。输入：问题 """
    try:
        result = RetrievalService.retrieve_with_citation(query, k=chroma_config['top_k'])
        return result

    except Exception as e:
        logger.info(f"search knowledge error:{str(e)}")
        return {}

ToolsRegistry.register(
    name='search_knowledge_base',
    description='搜索知识库，用于查询文档中的信息。输入：问题',
    func=_search_knowledge
)