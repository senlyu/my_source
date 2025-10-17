from abc import ABC, abstractmethod
from typing import final

class PromptFormat(ABC):

    @abstractmethod
    def get_format_prompt(self):
        pass

    @abstractmethod
    def make_standard(self, txt):
        pass

    @abstractmethod
    def format_validate(self, txt):
        pass


class PromptBase(PromptFormat, ABC):
    @abstractmethod
    def prompt(self):
        pass

    @final
    def get_prompt(self):
        return self.prompt() + self.get_format_prompt()