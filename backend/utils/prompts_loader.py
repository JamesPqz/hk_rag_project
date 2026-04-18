from backend.utils.config_handler import prompts_config
from backend.utils.path_tool import get_abs_path
from backend.utils.logger_handler import logger

def load_sys_prompt():
    try:
        path = get_abs_path(prompts_config['main_prompt_path'])
    except KeyError as e:
        logger.error(f'[load_sys_prompt] no main_prompt_path')
        raise e

    try:
        return open(path, 'r', encoding='utf-8').read()
    except Exception as e:
        logger.error(f'[load_sys_prompt] open path err.{str(e)}')
        raise e

def load_rag_prompt():
    try:
        path = get_abs_path(prompts_config['rag_summarize_prompt_path'])
    except KeyError as e:
        logger.error(f'[load_rag_prompt] no rag_summarize_prompt_path')
        raise e

    try:
        return open(path, 'r', encoding='utf-8').read()
    except Exception as e:
        logger.error(f'[load_rag_prompt] open path err.{str(e)}')
        raise e

def load_report_prompt():
    try:
        path = get_abs_path(prompts_config['report_prompt_path'])
    except KeyError as e:
        logger.error(f'[load_report_prompt] no report_prompt_path')
        raise e

    try:
        return open(path, 'r', encoding='utf-8').read()
    except Exception as e:
        logger.error(f'[load_report_prompt] open path err.{str(e)}')
        raise e

if __name__ == '__main__':
    # print(load_sys_prompt())
    print(load_rag_prompt())
    print(load_report_prompt())
