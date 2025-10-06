import os
from datetime import date
from export.hexo_blog_helper.python_run_shell import PythonRunShell
from util.logging_to_file import Logging

class HexoExporter:
    UPLOAD_COMMAND = ["npm", "run", "save"]
    FILE_NAME = "Daily_Financial_News_Report"
    TEMPLATE_POST = "export/hexo_blog_helper/template_post.md"

    def __init__(self, directory_path, post_path):
        self.directory_path = directory_path
        self.post_path = post_path

    def gen_file_name(self):
        today_date = date.today().isoformat()
        return self.FILE_NAME + today_date + ".md"

    def generate_file(self, txt_in_array):
        file_name = self.gen_file_name()
        file_path = os.path.join(self.post_path, file_name)

        template_post = os.path.join(self.TEMPLATE_POST)

        with open(template_post, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            f.close()

        if os.path.isfile(file_path):
            os.remove(file_path)

        with open(file_path, 'w+', encoding="utf-8") as f:
            for line in lines:
                f.write(line)

            for txt in txt_in_array:
                f.write(f'{txt}')
            f.close()
        
    def hexo_upload(self):
        PythonRunShell.run_commandline(self.directory_path, self.UPLOAD_COMMAND)

    def export_by_model(self, messages, analyse):
        result = analyse.make_standard(messages)
        self.generate_file(result)
        self.hexo_upload()
        return result

    def export(self, text):
        Logging.log(text)

    