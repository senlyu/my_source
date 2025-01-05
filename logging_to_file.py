
import os
from datetime import datetime

class Logging:

    @staticmethod
    def clean():
        with open("log.txt", "a") as f:
            f.truncate(0)

    @staticmethod
    def log(*args, **kwargs):
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("log.txt", "a") as f:
            s = time + ": " + (" ").join(str(arg) for arg in args)
            s = s + (" ").join(str(f"{k}: {v}") for k, v in kwargs.items())
            f.write(s)
            f.write("\n")