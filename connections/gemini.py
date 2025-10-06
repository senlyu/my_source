import google.generativeai as genai
import base64
import time
from util.logging_to_file import Logging
from connections.model_api import ModelAPI

class GeminiConnect(ModelAPI):
    def __init__(self, api_key, promot):
        self.api_key = api_key
        self.promot = promot

    def make_standard(self, txt):
        return self.promot.make_standard(txt)

    def get_result_for_files(self, doc_paths, model_name):
        doc_data = ""
        for doc_path in doc_paths:
            with open(doc_path, "rb") as doc_file:
                doc_data += base64.standard_b64encode(doc_file.read()).decode("utf-8")

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(model_name) # "gemini-2.5-flash"

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, self.promot.get_promot()])

        return response

    def get_result_from_models(self, doc_paths):
        # try model "gemini-2.5-pro"
        try:
            response = self.get_result_for_files(doc_paths, "gemini-2.5-pro")
            msg = response.text
            (e, status) = self.promot.format_validate(msg)
            if not status:
                raise e
        except Exception as e:
            Logging.log(e)
            msg = None

        if (msg!="" and msg is not None):
            Logging.log("2.5 pro return results")
            req = { "model": "gemini-2.5-pro",  "doc_paths": doc_paths, "promot": self.promot.get_promot() }
            return (response, req)

        # try model "gemini-2.5-flash" with format enforcement
        for i in range(5):
            response = self.get_result_for_files(doc_paths, "gemini-2.5-flash")
            msg = response.text
            (e, status) = self.promot.format_validate(msg)
            if not status:
                Logging.log(e)
                continue
            if (msg!="" and msg is not None):
                Logging.log("2.5 flash return results")
                req = { "model": "gemini-2.5-flash",  "doc_paths": doc_paths, "promot": self.promot.get_promot() }
                return (response, req)
            Logging.log(f"2.5 flash return nothing, retry in {2**i*30} seconds...")
            time.sleep(2**i * 30) #retry

        # try model "gemini-2.5-flash" without format enforcement
        for i in range(5):
            response = self.get_result_for_files(doc_paths, "gemini-2.5-flash")
            msg = response.text
            (e, status) = self.promot.format_validate(msg)
            if (msg!="" and msg is not None):
                Logging.log("2.5 flash return results")
                req = { "model": "gemini-2.5-flash",  "doc_paths": doc_paths, "promot": self.promot.get_promot() }
                return (response, req)
            Logging.log(f"2.5 flash return nothing, retry in {2**i*30} seconds...")
            time.sleep(2**i * 30) #retry