# there are cases where the asan would detect multiple errors
import os
from enum import Enum, auto
import re


# attempted double-free
# dynamic-stack-buffer-overflow
# heap-buffer-overflow
# heap-use-after-free
# index out of bounds
# load of misaligned address
# load of null pointer
# member access within misaligned address
# member access within null pointer
# SEGV on unknown address
# signed integer overflow
# stack-overflow
# stack-buffer-overflow
# stack-buffer-underflow
# store to misaligned address
# store to null pointer
# unsigned integer overflow
# use-of-uninitialized-value

class ErrorType(Enum):
    # runtime errors
    UNDEFINED_BEHAVIOUR = auto()
    NULL_POINTER = auto()
    DIVISION_BY_ZERO = auto()
    LOAD_OF_VALUE = auto()

    INVALID_SHIFT = auto()
    INDEX_OUT_OF_BOUNDS = auto()
    MISALIGNED_ADDRESS = auto()

    FLOAT_CAST_OVERFLOW = auto()
    SIGNED_INTEGER_OVERFLOW = auto()

    # sanitizers
    ATTEMPT_DOUBLE_FREE = auto()
    DYNAMIC_STACK_BUFFER_OVERFLOW = auto()
    HEAP_USE_AFTER_FREE = auto()
    HEAP_BUFFER_OVERFLOW = auto()

    STACK_BUFFER_OVERFLOW = auto()
    STACK_BUFFER_UNDERFLOW = auto()
    STACK_USE_AFTER_SCOPE = auto()
    STACK_USE_AFTER_RETURN = auto()

    SIG_SEGV = auto()
    SIG_BUS = auto()


def categorise_error(error_message: str):
    errors = set()
    if re.search(r"UndefinedBehaviourSanitizer: undefined-behaviour", error_message):
        errors.add(ErrorType.UNDEFINED_BEHAVIOUR)
    if re.search(r"runtime error:.+null pointer", error_message):
        errors.add(ErrorType.NULL_POINTER)
    if re.search(r"runtime error: division by zero", error_message):
        errors.add(ErrorType.DIVISION_BY_ZERO)
    if re.search(r"runtime error: load of value", error_message):
        errors.add(ErrorType.LOAD_OF_VALUE)
    if re.search(r"runtime error:.+shift", error_message):
        errors.add(ErrorType.INVALID_SHIFT)
    if re.search(r"runtime error: index.+out of bounds", error_message):
        errors.add(ErrorType.INDEX_OUT_OF_BOUNDS)
    if re.search(r"runtime error:.+misaligned address", error_message):
        errors.add(ErrorType.MISALIGNED_ADDRESS)
    if re.search(r"runtime error: signed integer overflow", error_message):
        errors.add(ErrorType.SIGNED_INTEGER_OVERFLOW)

    if re.search(r"AddressSanitizer:.+double-free", error_message):
        errors.add(ErrorType.ATTEMPT_DOUBLE_FREE)
    if re.search(r"AddressSanitizer: dynamic-stack-buffer-overflow", error_message):
        errors.add(ErrorType.DYNAMIC_STACK_BUFFER_OVERFLOW)
    if re.search(r"AddressSanitizer: heap-use-after-free", error_message):
        errors.add(ErrorType.HEAP_USE_AFTER_FREE)
    if re.search(r"AddressSanitizer: heap-buffer-overflow", error_message):
        errors.add(ErrorType.HEAP_BUFFER_OVERFLOW)

    if re.search(r"AddressSanitizer: stack-buffer-overflow", error_message):
        errors.add(ErrorType.STACK_BUFFER_OVERFLOW)
    if re.search(r"AddressSanitizer: stack-buffer-underflow", error_message):
        errors.add(ErrorType.STACK_BUFFER_UNDERFLOW)
    if re.search(r"AddressSanitizer: stack-use-after-scope", error_message):
        errors.add(ErrorType.STACK_USE_AFTER_SCOPE)
    if re.search(r"AddressSanitizer: stack-use-after-return", error_message):
        errors.add(ErrorType.STACK_USE_AFTER_SCOPE)

    if re.search(r"AddressSanitizer: SEGV on unknown address", error_message):
        errors.add(ErrorType.SIG_SEGV)

    if re.search(r"AddressSanitizer: BUS on unknown address", error_message):
        errors.add(ErrorType.SIG_BUS)

    return errors


if __name__ == '__main__':
    with open(os.path.join('error_logs', 'error_0.cng')) as f:
        print(categorise_error(f.read()))
        # with open(os.path.join('error_logs', 'error_11.cng')) as f2:
        #     similarity = similar(f.read(), f2.read())
        #     print(similarity)
