from google import genai
from google.genai.errors import APIError
import os
import time
import datetime
from ..util.logging_standard import DefaultLogger as Logging
from ..util.session_context import SessionIDHelper
from ..data_io.save_to_file import SaveToFile, hash_data_40_chars

logger = Logging.getLogger(__name__)

class GeminiConnect:
    EXPENSIVE_MODEL = "gemini-2.5-pro"
    BACKUP_MODEL = "gemini-2.5-flash"
    BACKUP_MODEL_2 = "gemini-2.0-flash"

    def __init__(self, key_manager, history=None):
        self.history = history
        self.key_manager = key_manager
        self.clean_history()

    def data_load_from_path(self, doc_paths):
        doc_data_parts = []
        for doc_path in doc_paths:
            with open(doc_path, "r", encoding="utf-8") as doc_file:
                txt_data = doc_file.read()
                doc_data_parts.append(txt_data)
        return "".join(doc_data_parts)

    async def get_result_from_model_with_files_async_text(self, prompt, other_data, model_name):
        try:
            logger.info("Try to get api_key for continue...")
            api_key = await self.key_manager.get_key_and_wait()
            logger.info("api_key get, start request")

            client = genai.Client(api_key=api_key)
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=[
                    *other_data,
                    prompt.get_prompt(),
                ]
            )
            return response
        finally:
            self.key_manager.release_key(api_key)
            logger.info("api_key released")

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
                    logger.error(e)
                    continue

    async def get_result_from_model_by_type(self, prompt, other_data, data_configs, model_type, validation_needed=False):
        req = { "model": model_type,  "configs": data_configs, "prompt": prompt.get_prompt() }
        txt = None
        usage_metadata = None

        # try cache
        previous_res = self.load_from_history(prompt, data_configs, model_type)
        if previous_res is not None:
            logger.info(f"{model_type} find result from cache")
            txt = previous_res
        else:
            # try model
            try:
                logger.info(f"Start to get model result: {req}")
                response = await self.get_result_from_model_with_files_async_text(prompt, other_data, model_type)
                txt = response.text
                usage_metadata = response.usage_metadata
                if validation_needed:
                    (e, status) = prompt.validate_formated_result(txt)
                    if not status:
                        raise e
            except APIError as e:
                if "429 RESOURCE_EXHAUSTED" in str(e):
                    logger.warning("quota limit")
                logger.error(e)
                txt = None
            except Exception as e:
                logger.error(e)
                txt = None
            
            if (txt!="" and txt is not None):
                logger.info(f"{model_type} return results")
                self.save_to_history(txt, prompt, data_configs, model_type)
        
        return ({"txt": txt, "usage_metadata": usage_metadata}, req)


    async def get_result_from_models(self, prompt, other_data, data_related_configs):
        # try expensive model
        (result, req) = await self.get_result_from_model_by_type(prompt, other_data, data_related_configs, self.EXPENSIVE_MODEL, True)
        if result["txt"] is not None and result["txt"] != "":
            return (result, req)
        
        # try bakcup model with format enforcement
        for i in range(5):
            (result, req) = await self.get_result_from_model_by_type(prompt, other_data, data_related_configs, self.BACKUP_MODEL, True)
            if result["txt"] is not None and result["txt"] != "":
                return (result, req)
            
            time.sleep(2**i * 30) #retry

        # try backup model without format enforcement
        for i in range(5):
            (result, req) = await self.get_result_from_model_by_type(prompt, other_data, data_related_configs, self.BACKUP_MODEL_2, False)
            if result["txt"] is not None and result["txt"] != "":
                return (result, req)
            
            time.sleep(2**i * 30) #retry

    async def get_standard_result_from_model(self, prompt, all_msgs, data_configs):
        session = SessionIDHelper()
        session.create_session_id()
        try:
            (result, req) = await self.get_result_from_models(prompt, ["".join(all_msgs[0])], data_configs)
            logger.info(req)
            logger.info(result)
            logger.info(f"{req["model"]}")
            logger.info(f"{result["usage_metadata"]}")
            result = prompt.header() + prompt.get_formated_result(result["txt"])
        finally:
            session.reset_session_id()


        return result