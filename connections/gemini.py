import google.generativeai as genai
import os
import base64
import time
import datetime
from util.logging_to_file import Logging
from storage.save_to_file import SaveToFile, hash_data_40_chars

class GeminiConnect:
    EXPENSIVE_MODEL = "gemini-2.5-pro"
    BACKUP_MODEL = "gemini-2.5-flash"

    def __init__(self, api_key, history=None):
        self.api_key = api_key
        self.history = history
        self.clean_history()

    def get_result_from_model_with_files(self, prompt, doc_paths, model_name):
        doc_data_parts = []
        for doc_path in doc_paths:
            with open(doc_path, "rb") as doc_file:
                encoded_content = base64.standard_b64encode(doc_file.read()).decode("utf-8")
                doc_data_parts.append(encoded_content)

        doc_data = "".join(doc_data_parts)

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(model_name) # "gemini-2.5-flash"

        response = model.generate_content([{'mime_type': 'text/plain', 'data': doc_data}, prompt.get_prompt()])

        return response

    def load_from_history(self, prompt, doc_paths, model_name):
        if not hasattr(self, "history"):
            return None

        file_name = hash_data_40_chars({"doc_paths": doc_paths, "model_name": model_name, "prompt": prompt.get_prompt()})
        # find files
        for _, _, files in os.walk(self.history):
            for file in files:
                if file[10:-4] == file_name: # "2000-01-01xyz.txt"[10:-4] = "xyz" 
                    path = os.path.join(self.history, file)
                    storage = SaveToFile(path)
                    return storage.load()
        
        return None

    def save_to_history(self, data, prompt, doc_paths, model_name):
        if not hasattr(self, "history"):
            return None
        
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        params = hash_data_40_chars({"doc_paths": doc_paths, "model_name": model_name, "prompt": prompt.get_prompt()})
        path = os.path.join(self.history, date+params+".txt")
        storage = SaveToFile(path)
        return storage.save(data)

    def clean_history(self):
        if not hasattr(self, "history"):
            return None
        
        for _, _, files in os.walk(self.history):
            for file in files:
                file_date = file[:10]
                try:
                    date_obj_file = datetime.datetime.strptime(file_date, '%Y-%m-%d')
                    if date_obj_file + datetime.timedelta(days=30) < datetime.datetime.now():
                        os.remove(os.path.join(self.history, file))
                except Exception as e:
                    Logging.log(e)
                    continue

    def get_result_from_model_by_type(self, prompt, doc_paths, model_type, validation_needed=False):
        req = { "model": model_type,  "doc_paths": doc_paths, "prompt": prompt.get_prompt() }
        txt = None
        usage_metadata = None

        # try cache
        data = self.load_from_history(prompt, doc_paths, model_type)
        if data is not None:
            Logging.log(f"{model_type} find result from cache")
            txt = data
        else:
            # try model
            try:
                response = self.get_result_from_model_with_files(prompt, doc_paths, model_type)
                txt = response.text
                usage_metadata = response.usage_metadata
                if validation_needed:
                    (e, status) = prompt.validate_formated_result(txt)
                    if not status:
                        raise e
            except Exception as e:
                Logging.log(e)
                txt = None
            
            if (txt!="" and txt is not None):
                Logging.log(f"{model_type} return results")
                self.save_to_history(txt, prompt, doc_paths, model_type)
        
        return ({"txt": txt, "usage_metadata": usage_metadata}, req)


    def get_result_from_models(self, prompt, doc_paths):
        # try expensive model
        (result, req) = self.get_result_from_model_by_type(prompt, doc_paths, self.EXPENSIVE_MODEL, True)
        if result["txt"] is not None and result["txt"] != "":
            return (result, req)
        
        # try bakcup model with format enforcement
        for i in range(5):
            (result, req) = self.get_result_from_model_by_type(prompt, doc_paths, self.BACKUP_MODEL, True)
            if result["txt"] is not None and result["txt"] != "":
                return (result, req)
            
            time.sleep(2**i * 30) #retry

        # try backup model without format enforcement
        for i in range(5):
            (result, req) = self.get_result_from_model_by_type(prompt, doc_paths, self.BACKUP_MODEL, False)
            if result["txt"] is not None and result["txt"] != "":
                return (result, req)
            
            time.sleep(2**i * 30) #retry