import logging

from typing import Callable, Generator, Literal, Union, overload

from flask import Flask

from configs import app_config
from extensions.storage.base_storage import BaseStorage
from extensions.storage.storage_type import StorageType

logger = logging.getLogger(__name__)

class Storage:
    
    def init_app(self, app: Flask):
        storage_factory = self.get_storage_factory(app_config.STORAGE_TYPE)
        with app.app_context():
            self.storage_runner = storage_factory()
            
    @staticmethod
    def get_storage_factory(storage_type: str) -> Callable[[], BaseStorage]:
        match storage_type:
            case StorageType.MINIO:
                from extensions.storage.minio_storage import MinioStorage
                return MinioStorage
            
            case _:
                raise ValueError(f"Invalid storage type: {storage_type}")
        
    def save(self, filename: str, data: bytes):
        self.storage_runner.save(filename, data)
        
    @overload
    def load(self, filename: str, /, *, stream: Literal[False] = False) -> bytes: ...
    
    @overload
    def load(self, filename: str, /, *, stream: Literal[True]) -> Generator: ...
        
    def load(self, filename: str, /, *, stream: bool = False) -> Union[bytes, Generator]:
        if stream:
            return self.load_stream(filename)
        else:
            return self.load_once(filename)
        
    def load_once(self, filename: str) -> bytes:
        return self.storage_runner.load_once(filename)

    def load_stream(self, filename: str) -> Generator:
        return self.storage_runner.load_stream(filename)

    def download(self, filename, target_filepath):
        self.storage_runner.download(filename, target_filepath)

    def exists(self, filename):
        return self.storage_runner.exists(filename)

    def delete(self, filename: str):
        return self.storage_runner.delete(filename)

    def scan(self, path: str, files: bool = True, directories: bool = False) -> list[str]:
        return self.storage_runner.scan(path, files=files, directories=directories)
    
    
storage = Storage()

def init_app(app: Flask):
    storage.init_app(app)