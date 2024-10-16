# there are cases where the asan would detect multiple errors
from enum import Enum

class ErrorType(Enum):
    UNIDENTIFIED = 0,
    BUS = 1,
    SEGV = 2,
    OVERFLOW = 3,
    ERROR_END = 4,


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
