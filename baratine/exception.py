class BaratineException(Exception):
    def __init__(self, msg, cause = None):
        self.msg = msg
        self.cause = cause
