from .prompt_base import PromptFormatBase
from ...util.logging_to_file import Logging
import re

def check_headings(txt):
    h1_found = False
    h2_found = False
    
    # Check for H1 headings
    if re.search(r'^#\s', txt, re.MULTILINE):
        h1_found = True
        
    # Check for H2 headings
    if re.search(r'^##\s', txt, re.MULTILINE):
        h2_found = True
        
    return h1_found, h2_found

class HeaderFormat(PromptFormatBase):
    PROMPT_FORMAT_HEADER = "所有标题使用markdown H3 ###及以下形式，禁止使用#或者##的大标题"

    @staticmethod
    def get_format_prompt():
        return HeaderFormat.PROMPT_FORMAT_HEADER
    
    @staticmethod
    def make_standard(txt):
        Logging.log(txt)
        return txt

    @staticmethod
    def format_validate(txt):
        try:
            h1_found, h2_found = check_headings(txt)
            if h1_found or h2_found:
                raise ValueError(f"format not match, contains h1 {h1_found} or h2 {h2_found}")
            else:
                return (None, True)
        except Exception as e:
            return (e, False)