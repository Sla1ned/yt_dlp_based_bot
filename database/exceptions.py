class DataBaseError(Exception):
    pass

class MaxRetriesExceededError(DataBaseError):
    pass