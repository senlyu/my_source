from prompts.prompt_base import PromptFormat
from util.logging_to_file import Logging

class StarterFormat(PromptFormat):
    PROMPT_FORMAT_SP = "正文部分开始之前用另起一行的<start>做提示，不要用‘作为美股分析师，我为您总结了xxx’等任何语句作为开头。直接以一个标题开始"

    def get_format_prompt(self):
        return self.PROMPT_FORMAT_SP
    
    def make_standard(self, txt):
        Logging.log([txt])
        index = txt.find("<start>")
        txt = txt[index+7:]
        return [txt]

    def format_validate(self, txt):
        index = txt.find("<start>")
        if index == -1:
            return (ValueError("format not match, no <start>"), False)
        else:
            return (None, True)