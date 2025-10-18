from .prompt_base import PromptBase
from .empty_format import EmptyFormat
from .starter_format import StarterFormat
from .sp_format import SPFormat

PROMPT = "我是一名美股分析师，我在收集每日重要信息并且帮助我生成财经新闻报告。用中文，第一部分尽可能简短的描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。如果有政府，美联储官员等重要消息源头，再详述内容，确保明确保留其观点内容数据等详细信息，不可省略。第一部分时间包括昨日和今日。在第二部分，再用中文详细提供短期股票市场相关新闻，时间仅保留今日信息，保留详细数字和数据，重点保留美国数据，并且保留所有有关股票的数据和数字，股票代号用英文。避免开头和结尾不必要的声明和上下文回复"

class FinancePrompt:
    def prompt(self):
        return PROMPT

class GeminiPromptNoFormat(FinancePrompt, PromptBase):
    def __init__(self, prompt_formats = None):
        if prompt_formats is None:
            prompt_formats = []
        prompt_formats.append(EmptyFormat)
        super().__init__(prompt_formats)

class GeminiPromptWithSP(FinancePrompt, PromptBase):
    def __init__(self, prompt_formats = None):
        if prompt_formats is None:
            prompt_formats = []
        prompt_formats.append(SPFormat)
        super().__init__(prompt_formats)


NEW_PROMPT_FIRST_PART = "我是一名美股分析师，请按照以下要求从附带的信息中总结以下内容。用中文，描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。"
NEW_PROMPT_SECOND_PART = "我是一名美股分析师，请按照以下要求从附带的信息中总结以下内容。用中文，总结政府，美联储官员等重要消息源头，再详述内容，确保明确保留其观点内容数据等详细信息。"
NEW_PROMPT_THIRD_PART = "我是一名美股分析师，请按照以下要求从附带的信息中总结以下内容。用中文，详细提供美国股票市场今日主要企业的相关信息，关注科技，半导体，金融等行业，聚焦财报或者业务变动情况，忽略股价变化，保留详细数字和数据，忽略id，股票代号用英文。"
NEW_PROMPT_FOURTH_PART = "我是一名美股分析师，请按照以下要求从附带的信息中总结以下内容。用中文，详细提供短期美国股票今日股价的变动信息，保留详细数字和数据，重点关注美国数据，并且保留所有有关股票数据变化，忽略企业业务变化等描述，忽略id，股票代号用英文。"
NEW_PROMPT_FIFTH_PART = "我是一名美股分析师，请按照以下要求从附带的信息中总结以下内容。用中文，详细提供今日虚拟货币的相关信息，保留详细数字和数据，忽略id，代号用英文。"

class FinancePromptWithStarterFormat(PromptBase):
    def __init__(self, prompt_formats = None):
        if prompt_formats is None:
            prompt_formats = []
        prompt_formats.append(StarterFormat)
        super().__init__(prompt_formats)

class FinancePromptFirstPart(FinancePromptWithStarterFormat):
    def prompt(self):
        return NEW_PROMPT_FIRST_PART

class FinancePromptSecondPart(FinancePromptWithStarterFormat):
    def prompt(self):
        return NEW_PROMPT_SECOND_PART

class FinancePromptThirdPart(FinancePromptWithStarterFormat):
    def prompt(self):
        return NEW_PROMPT_THIRD_PART

class FinancePromptFourthPart(FinancePromptWithStarterFormat):
    def prompt(self):
        return NEW_PROMPT_FOURTH_PART

class FinancePromptFifthPart(FinancePromptWithStarterFormat):
    def prompt(self):
        return NEW_PROMPT_FIFTH_PART