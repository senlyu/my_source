from prompts.prompt_base import PromptBase
from prompts.empty_format import EmptyFormat
from prompts.sp_format import SPFormat

PROMPT = "我是一名美股分析师，我在收集每日重要信息并且帮助我生成财经新闻报告。用中文，第一部分尽可能简短的描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。如果有政府，美联储官员等重要消息源头，再详述内容，确保明确保留其观点内容数据等详细信息，不可省略。第一部分时间包括昨日和今日。在第二部分，再用中文详细提供短期股票市场相关新闻，时间仅保留今日信息，保留详细数字和数据，重点保留美国数据，并且保留所有有关股票的数据和数字，股票代号用英文。避免开头和结尾不必要的声明和上下文回复"

class FinancePrompt:
    def prompt(self):
        return PROMPT

class GeminiPromptNoFormat(FinancePrompt, EmptyFormat, PromptBase):
    pass

class GeminiPromptWithSP(FinancePrompt, SPFormat, PromptBase):
    pass