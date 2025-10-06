from promots.promot_base import PromotFormat

class EmptyFormat(PromotFormat):
    PROMOT_FORMAT_SP = ""

    def get_format_promot(self):
        return self.PROMOT_FORMAT_SP
    
    def make_standard(self, txt):
        return txt

    def format_validate(self, txt):
        return (None, True)