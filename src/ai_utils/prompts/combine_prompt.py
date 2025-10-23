from src.ai_utils.prompts.prompt_base import PromptBase

PROMPT = "这是我用相同的格式不同的文本拿到的所有信息，我希望将他们全部合并起来。请保留所有信息，不要遗漏任何信息，但需要避免重复内容，输出的总字符数应该非常接近输入的全部文本总字符数。这些信息应仍然保持相似的内容结构。"

class CombinePrompt(PromptBase):
    def __init__(self, prompt_formats = None):
        if prompt_formats is None:
            prompt_formats = []
        super().__init__(prompt_formats)
    
    @staticmethod
    def header():
        return ""

    def prompt(self):
        return PROMPT