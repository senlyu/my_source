import google.generativeai as genai
import base64

class GeminiConnect:
    PROMOT = "用中文，第一部分尽可能简短的描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。在第二部分，再用中文详细提供短期股票市场波动相关新闻，保留详细数据，重点保留美国数据，并且保留所有有关股票的数据。"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_result_for_files(self, doc_paths):
        doc_data = ""
        for doc_path in doc_paths:
            with open(doc_path, "rb") as doc_file:
                doc_data += base64.standard_b64encode(doc_file.read()).decode("utf-8")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, self.PROMOT])

        return response