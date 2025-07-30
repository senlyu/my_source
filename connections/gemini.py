import google.generativeai as genai
import base64

class GeminiConnect:
    PROMOT = "用中文，第一部分尽可能简短的描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。如果有政府，美联储官员等重要消息源头，再详述内容，确保明确保留其观点内容数据等详细信息，不可省略。第一部分时间包括昨日和今日。在第二部分，再用中文详细提供短期股票市场相关新闻，时间仅保留今日信息，保留详细数字和数据，重点保留美国数据，并且保留所有有关股票的数据和数字，股票代号用英文。"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_result_for_files(self, doc_paths):
        doc_data = ""
        for doc_path in doc_paths:
            with open(doc_path, "rb") as doc_file:
                doc_data += base64.standard_b64encode(doc_file.read()).decode("utf-8")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-2.5-pro")

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, self.PROMOT])

        return response