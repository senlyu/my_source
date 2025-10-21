import os
from datetime import date
from .hexo_blog_helper.python_run_shell import PythonRunShell

class HexoExporter:
    FILE_NAME = "Daily_Financial_News_Report"
    TEMPLATE_POST = "src/data_io/hexo_blog_helper/template_post.md"

    def __init__(self, directory_path, post_path, web_domain_url, upload_command, command_path, report_name=None, tag=None):
        self.directory_path = directory_path
        self.post_path = post_path
        self.web_domain_url = web_domain_url
        self.upload_command = upload_command
        self.command_path = command_path
        self.report_name = report_name if report_name is not None else self.FILE_NAME
        self.tag = tag

    def get_file_name(self):
        today_date = date.today().isoformat()
        return self.report_name + today_date + ".md"

    def get_new_post_link(self):
        return (self.web_domain_url + self.get_file_name())[:-3] # remove .md
    
    def gen_replace_from_template(self, temp_string):
        res = temp_string
        if res.find("<TITLE>") != -1:
            res = res.replace("<TITLE>", self.report_name)
        
        if res.find("<TAG>") != -1:
            if self.tag is not None:
                res = res.replace("<TAG>", self.tag)
            else:
                res = ""
        return res

    def generate_file(self, txt_in_array):
        file_name = self.get_file_name()
        file_path = os.path.join(self.post_path, file_name)

        template_post = os.path.join(self.TEMPLATE_POST)

        with open(template_post, 'r', encoding="utf-8") as f:
            lines = f.readlines()
            f.close()

        if os.path.isfile(file_path):
            os.remove(file_path)

        with open(file_path, 'w+', encoding="utf-8") as f:
            for line in lines:
                line = self.gen_replace_from_template(line)
                f.write(line)

            for txt in txt_in_array:
                f.write(f'{txt}')
            f.close()
        
    def hexo_upload(self):
        PythonRunShell.run_commandline(self.directory_path, self.upload_command, self.command_path)

    def export(self, messages):
        self.generate_file(messages)
        self.hexo_upload()
        return messages
    