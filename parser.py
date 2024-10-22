# there are cases where the asan would detect multiple errors
import os
from enum import Enum, auto
import re

class ErrorType(Enum):
    UNDEFINED_BEHAVIOR = auto()
    INVALID_SHIFT = auto()
    DIVISION_BY_ZERO = auto()
    NULL_POINTER = auto()
    INDEX_OUT_OF_BOUNDS = auto()
    MISALIGNED_POINTER = auto()
    FLOAT_CAST_OVERFLOW = auto()
    SIGNED_INTEGER_OVERFLOW = auto()
    USE_AFTER_FREE = auto()
    SIG_SEGV = auto()
    SIG_BUS = auto()
    USE_AFTER_RETURN = auto()
    BUFFER_OVERFLOW = auto()
    STACK_BUFFER_OVERFLOW = auto()
    HEAP_BUFFER_OVERFLOW = auto()
    GLOBAL_BUFFER_OVERFLOW = auto()
    DOUBLE_FREE = auto()
    INVALID_FREE = auto()
    MEMORY_LEAK = auto()


def categorise_error(error_message: str):
    errors = set()
    if re.search(r"null.*pointer", error_message, re.IGNORECASE):
        errors.add(ErrorType.NULL_POINTER)

    if re.search(r"AddressSanitizer: SEGV on unknown address", error_message, re.IGNORECASE):
        errors.add(ErrorType.SIG_SEGV)
    if re.search(r"AddressSanitizer: heap-buffer-overflow", error_message, re.IGNORECASE):
        errors.add(ErrorType.HEAP_BUFFER_OVERFLOW)
    if re.search(r"AddressSanitizer: BUS on unknown address", error_message, re.IGNORECASE):
        errors.add(ErrorType.SIG_BUS)
    return errors

if __name__ == '__main__':
    with open(os.path.join('error_logs', 'error_0.cng')) as f:
        print (categorise_error(f.read()))
        # with open(os.path.join('error_logs', 'error_11.cng')) as f2:
        #     similarity = similar(f.read(), f2.read())
        #     print(similarity)