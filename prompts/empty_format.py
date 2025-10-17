from prompts.prompt_base import PromptFormat
from util.logging_to_file import Logging

class EmptyFormat(PromptFormat):
    PROMPT_FORMAT_SP = ""

    def get_format_prompt(self):
        return self.PROMPT_FORMAT_SP
    
    def make_standard(self, txt):
        Logging.log([txt])
        return [txt]

    def format_validate(self, txt):
        return (None, True)