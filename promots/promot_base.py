from abc import ABC, abstractmethod
from typing import final

class PromotFormat(ABC):

    @abstractmethod
    def get_format_promot(self):
        pass

    @abstractmethod
    def make_standard(self, txt):
        pass

    @abstractmethod
    def format_validate(self, txt):
        pass


class PromotBase(PromotFormat, ABC):
    @abstractmethod
    def promot(self):
        pass

    @final
    def get_promot(self):
        return self.promot() + self.get_format_promot()