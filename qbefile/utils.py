import os.path

CONFIG_FILE_NAMES: list[str] = [
    'qbe.yml',
    'qbe.yaml'
]


def find_in(directory: str) -> str:
    for file in CONFIG_FILE_NAMES:
        path = os.path.join(os.path.expanduser(directory), file)
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(f'There is no qbe file in {directory}')
