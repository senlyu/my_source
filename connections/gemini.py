import google.generativeai as genai
import base64
import time
from logging_to_file import Logging
from typing import List
from connections.model_api import ModelAPI

class GeminiConnect(ModelAPI):
    PROMOT = "用中文，第一部分尽可能简短的描述全球重大事件，美国重大事件，经济重大事件，短期股票市场，货币市场，重金属，大宗商品趋势，忽略重复的新闻。如果有政府，美联储官员等重要消息源头，再详述内容，确保明确保留其观点内容数据等详细信息，不可省略。第一部分时间包括昨日和今日。在第二部分，再用中文详细提供短期股票市场相关新闻，时间仅保留今日信息，保留详细数字和数据，重点保留美国数据，并且保留所有有关股票的数据和数字，股票代号用英文。使用<SP>作为分隔符,每大约1000字符的内容用<SP>来分开,每部分不可以超过1500字符"

    @staticmethod
    def get_chunk_by_split(string: str, signal: str ="<SP>") -> List[str]:
        return string.split(signal)

    def __init__(self, api_key):
        self.api_key = api_key

    def get_result_for_files(self, doc_paths, model_name):
        doc_data = ""
        for doc_path in doc_paths:
            with open(doc_path, "rb") as doc_file:
                doc_data += base64.standard_b64encode(doc_file.read()).decode("utf-8")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(model_name) # "gemini-2.5-flash"

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, self.PROMOT])

        return response

    def get_result_from_models(self, doc_paths):
        # try model "gemini-2.5-pro"
        response = self.get_result_for_files(doc_paths, "gemini-2.5-pro")
        msg = response.text

        if (msg!="" and msg is not None):
            Logging.log("2.5 pro return results")
            req = { "model": "gemini-2.5-pro",  "doc_paths": doc_paths, "promot": self.PROMOT }
            return (response, req)

        # try model "gemini-2.5-flash"
        for i in range(5):
            response = self.get_result_for_files(doc_paths, "gemini-2.5-flash")
            msg = response.text
            if (msg!="" and msg is not None):
                Logging.log("2.5 flash return results")
                req = { "model": "gemini-2.5-flash",  "doc_paths": doc_paths, "promot": self.PROMOT }
                return (response, req)
            Logging.log(f"2.5 flash return nothing, retry in {2**i*30} seconds...")
            time.sleep(2**i * 30) #retry