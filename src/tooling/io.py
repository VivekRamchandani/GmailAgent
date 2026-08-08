from pathlib import Path

class IsNotADirectoryError(IOError): pass

class FileIOTools():

    def __init__(self, base_path: str, create_mode: bool = True):
        self.base_path = Path(base_path)

        if create_mode:
            self.base_path.mkdir()

        if not self.base_path.exists:
            raise FileNotFoundError(f"Path {base_path} doesn't exists")
        if not self.base_path.is_dir():
            raise IsNotADirectoryError(f"Path {base_path} isn't a directory")
        
    def list_content(self) -> list[str]:
        contents = [content.name for content in self.base_path.iterdir()]
        return contents

    def create_file(self, name: str, path: str):
        pass

    def delete_file(self, path: str):
        pass

    def read_file(self, path: str) -> str:
        pass

    def write_file(self, path: str, content: str):
        pass