
class OpenAIConnect:
    PROMOT = "全球重大事件，美国重大事件，经济重大事件，短期股票市场波动，货币市场，重金属，大宗商品趋势，尽可能简短"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_promot(self):
        return self.PROMOT
