from abc import ABC, abstractmethod
from typing import List

class PromptFormatBase(ABC):
    @staticmethod
    def get_format_prompt():
        raise NotImplementedError()

    @staticmethod
    def make_standard(txt):
        raise NotImplementedError()

    @staticmethod
    def format_validate(txt) -> tuple[Exception, bool]:
        raise NotImplementedError()

class PromptBase(ABC):
    def __init__(self, prompt_formats: List[PromptFormatBase] = None):
        if prompt_formats is None:
            prompt_formats = []
        self.prompt_formats = prompt_formats

    @abstractmethod
    def prompt(self):
        raise NotImplementedError()

    def get_prompt(self):
        format_prompt = ".".join([p_format.get_format_prompt() for p_format in self.prompt_formats])
        return self.prompt() + format_prompt
    
    def process_result(self, txt, do_validation):
        res = txt
        for p_format in self.prompt_formats[::-1]:
            if do_validation:
                (e, is_valid_format) = p_format.format_validate(res)
                if not is_valid_format:
                    return (e, is_valid_format, None)
            res = p_format.make_standard(res)
        return (None, True, res)
    
    def get_formated_result(self, txt):
        return self.process_result(txt, False)[2]
    
    def validate_formated_result(self, txt):
        (error, validation_result, _) = self.process_result(txt, True)
        return (error, validation_result)