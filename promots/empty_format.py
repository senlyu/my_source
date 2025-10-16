from promots.promot_base import PromotFormat
from util.logging_to_file import Logging

class EmptyFormat(PromotFormat):
    PROMOT_FORMAT_SP = ""

    def get_format_promot(self):
        return self.PROMOT_FORMAT_SP
    
    def make_standard(self, txt):
        Logging.log([txt])
        return [txt]

    def format_validate(self, txt):
        return (None, True)