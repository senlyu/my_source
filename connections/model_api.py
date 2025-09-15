from abc import ABC, abstractmethod
from typing import List

class ModelAPI(ABC):

    @staticmethod
    @abstractmethod
    def get_chunk_by_split(string: str, signal: str) -> List[str]:
        pass