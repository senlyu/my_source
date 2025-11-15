from .prompt_base import PromptFormatBase
from ...util.logging_standard import DefaultLogger as Logging
logger = Logging.getLogger(__name__)

class StarterFormat(PromptFormatBase):
    PROMPT_FORMAT_SP = "正文部分开始之前用另起一行的<start>做提示，不要用‘作为美股分析师，我为您总结了xxx’等任何语句作为开头。直接以一个标题开始"

    @staticmethod
    def get_format_prompt():
        return StarterFormat.PROMPT_FORMAT_SP
    
    @staticmethod
    def make_standard(txt):
        logger.debug(txt)
        index = txt.find("<start>")
        txt = txt[index+7:]
        return txt

    @staticmethod
    def format_validate(txt):
        try:
            index = txt.find("<start>")
            if index == -1:
                raise ValueError("format not match, no <start>")
            else:
                return (None, True)
        except Exception as e:
            return (e, False)
        
class StarterFormatV2(PromptFormatBase):
    PROMPT_FORMAT_SP = "在回答的第一个大标题前面增加<start>作为标志"

    @staticmethod
    def get_format_prompt():
        return StarterFormatV2.PROMPT_FORMAT_SP
    
    @staticmethod
    def make_standard(txt):
        logger.debug(txt)
        index = txt.find("<start>")
        txt = txt[index+7:]
        return txt

    @staticmethod
    def format_validate(txt):
        try:
            index = txt.find("<start>")
            if index == -1:
                raise ValueError("format not match, no <start>")
            else:
                return (None, True)
        except Exception as e:
            return (e, False)