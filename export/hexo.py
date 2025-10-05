import os
from datetime import date
from export.hexo_blog_helper.python_run_shell import PythonRunShell

class HexoExporter:
    UPLOAD_COMMAND = ["npm", "run", "upload"]
    FILE_NAME = "Daily_Financial_News_Report"
    TEMPLATE_POST = "export/hexo_blog_helper/template_post.md"

    def __init__(self, directory_path, post_path):
        self.directory_path = directory_path
        self.post_path = post_path

    def add_txt_into_file(self, txt):
        pass

    def generate_file(self, txt):
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

            f.write(f'{txt}')
            f.close()
        

    def hexo_upload(self):
        PythonRunShell.run_commandline(self.directory_path, self.UPLOAD_COMMAND)

    def export(self, text):
        self.generate_file(text)
        self.hexo_upload()


    def gen_file_name(self):
        today_date = date.today().isoformat()
        return self.FILE_NAME + today_date + ".md"