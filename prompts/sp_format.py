from prompts.prompt_base import PromptFormatBase
from util.logging_to_file import Logging

class SPFormat(PromptFormatBase):
    PROMPT_FORMAT_SP = "格式上全文使用<SP>作为分隔符,每大约1000字符的内容用<SP>来分开,分开的内容绝对不可以超过1500字符,不要因此省略输出的内容"

    @staticmethod
    def get_format_prompt():
        return SPFormat.PROMPT_FORMAT_SP
    
    @staticmethod
    def make_standard(txt):
        res = txt.split("<SP>")
        for r in res: 
            Logging.log(r)
        return "/n".join(res)

    @staticmethod
    def format_validate(txt):
        try:
            sections = txt.split("<SP>")
            for section in sections:
                if len(section) > 1500:
                    return (ValueError("section size is over 1500 chars"), False)

            return (None, True)
        except Exception as e:
            return (e, False)
