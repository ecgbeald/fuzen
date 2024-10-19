# there are cases where the asan would detect multiple errors
import os
from enum import Enum
from difflib import SequenceMatcher

class ErrorType(Enum):
    UNIDENTIFIED = 0,
    BUS = 1,
    SEGV = 2,
    OVERFLOW = 3,
    ERROR_END = 4,

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def is_error_different(error_message):
    for files in os.listdir('error_logs'):
        with open(os.path.join('error_logs', files)) as f:
            error = f.read()
            similarity = similar(error_message, error)
            if similarity > 0.3:
                return False
    return True

def parse_error(error_message):
    if "AddressSanitizer:" in error_message:
        if "BUS" in error_message:
            return ErrorType.BUS
        if "SEGV" in error_message:
            return ErrorType.SEGV
        if "OVERFLOW" in error_message:
            return ErrorType.OVERFLOW
        return ErrorType.UNIDENTIFIED
    return ErrorType.UNIDENTIFIED
    #     message = error_message.split("==ERROR:")[1]
    #     message = message.split("AddressSanitizer: ")[1]
    #     return message.split(" ")[0].strip()
    # else:
    #     return error_message.strip()

if __name__ == '__main__':
    with open(os.path.join('error_logs', 'error_8.cng')) as f:
        with open(os.path.join('error_logs', 'error_11.cng')) as f2:
            similarity = similar(f.read(), f2.read())
            print(similarity)