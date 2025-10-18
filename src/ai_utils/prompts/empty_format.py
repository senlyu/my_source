from .prompt_base import PromptFormatBase
from ...util.logging_to_file import Logging

class EmptyFormat(PromptFormatBase):
    PROMPT_FORMAT_SP = ""

    @staticmethod
    def get_format_prompt():
        return EmptyFormat.PROMPT_FORMAT_SP
    
    @staticmethod
    def make_standard(txt):
        Logging.log(txt)
        return txt

    @staticmethod
    def format_validate(txt):
        return (None, True)