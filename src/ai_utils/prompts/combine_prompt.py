from src.ai_utils.prompts.prompt_base import PromptBase
from src.ai_utils.prompts.starter_format import StarterFormatV2

PROMPT = "以上的内容存在多个重复的大标题每个大标题下面有对应的小标题。现在需要整合整个文档，仍然按照“宏观事件，重要人物言论，企业事件，股票市场，虚拟货币市场”的结构整合文档但各个大标题只出现一次，小标题也只出现一次，但所有的内容将整合到小标题之中，不要缩减文档的内容"

class CombinePrompt(PromptBase):
    def __init__(self, prompt_formats = None):
        if prompt_formats is None:
            prompt_formats = [StarterFormatV2]
        super().__init__(prompt_formats)
    
    @staticmethod
    def header():
        return ""

    def prompt(self):
        return PROMPT