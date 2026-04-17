import os

def get_project_root() -> str :
    current_file = os.path.abspath(__file__)
    # print(current_file)
    current_dir = os.path.dirname(current_file)
    # print(current_dir)
    project_root = os.path.dirname(current_dir)
    # print(project_root)
    return project_root

def get_abs_path(relative_path:str) -> str:
    project_root = get_project_root()
    return  os.path.join(project_root, relative_path)

if __name__ == '__main__':
    print(get_abs_path('config/agent.yml'))