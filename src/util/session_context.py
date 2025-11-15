
import contextvars
import uuid

DEFAULT_ID = "00000000"
SESSION_ID_VAR = contextvars.ContextVar("session_id", default=DEFAULT_ID)

class SessionIDHelper:
    def __init__(self):
        self.token = None

    def create_session_id(self):
        self.token = SESSION_ID_VAR.set(str(uuid.uuid4())[:len(DEFAULT_ID)])

    def reset_session_id(self):
        SESSION_ID_VAR.reset(self.token)
        self.token = None

    @staticmethod
    def get_session_id():
        return SESSION_ID_VAR.get()