from abc import ABC, abstractmethod

class ModelAPI(ABC):

    @abstractmethod
    def make_standard(self, txt):
        pass