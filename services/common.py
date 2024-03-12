import os


class DirectoryCreator:
    def __init__(self):
        if not os.path.exists('tests'):
            os.makedirs('tests')
        if not os.path.exists('data'):
            os.makedirs('data')
        directories = ['videos', 'maps']
        for directory in directories:
            if not os.path.exists(f'data/{directory}'):
                os.makedirs(f'data/{directory}')

    @staticmethod
    def new_directory(type_file: str, name: str) -> str:
        if not os.path.exists(f'data/{type_file}/{name}'):
            os.makedirs(f'data/{type_file}/{name}')
        return f'data/{type_file}/{name}'
