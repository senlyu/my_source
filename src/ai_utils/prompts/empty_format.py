from .prompt_base import PromptFormatBase
from ...util.logging_standard import DefaultLogger as Logging
logger = Logging.getLogger(__name__)
class EmptyFormat(PromptFormatBase):
    PROMPT_FORMAT_SP = ""

    @staticmethod
    def get_format_prompt():
        return EmptyFormat.PROMPT_FORMAT_SP
    
    @staticmethod
    def make_standard(txt):
        logger.debug(txt)
        return txt

    @staticmethod
    def format_validate(txt):
        return (None, True)