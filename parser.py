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

def match_single_ubsan_error(error_message: str):
    if re.match(r"UndefinedBehaviorSanitizer: undefined-behavior", error_message):
        return ErrorType.UNDEFINED_BEHAVIOUR

def match_single_asan_error(error_message: str):
    if re.search(r"AddressSanitizer:.+double-free", error_message):
        return ErrorType.ATTEMPT_DOUBLE_FREE
    if re.search(r"AddressSanitizer: dynamic-stack-buffer-overflow", error_message):
        return ErrorType.DYNAMIC_STACK_BUFFER_OVERFLOW
    if re.search(r"AddressSanitizer: heap-use-after-free", error_message):
        return ErrorType.HEAP_USE_AFTER_FREE
    if re.search(r"AddressSanitizer: heap-buffer-overflow", error_message):
        return ErrorType.HEAP_BUFFER_OVERFLOW

    if re.search(r"AddressSanitizer: stack-buffer-overflow", error_message):
        return ErrorType.STACK_BUFFER_OVERFLOW
    if re.search(r"AddressSanitizer: stack-buffer-underflow", error_message):
        return ErrorType.STACK_BUFFER_UNDERFLOW
    if re.search(r"AddressSanitizer: stack-use-after-scope", error_message):
        return ErrorType.STACK_USE_AFTER_SCOPE
    if re.search(r"AddressSanitizer: stack-use-after-return", error_message):
        return ErrorType.STACK_USE_AFTER_SCOPE

    if re.search(r"AddressSanitizer: SEGV", error_message):
        return ErrorType.SIG_SEGV

    if re.search(r"AddressSanitizer: BUS", error_message):
        return ErrorType.SIG_BUS

def match_single_runtime_error(error_message: str):
    if re.search(r"runtime error:.+null pointer", error_message):
        return ErrorType.NULL_POINTER
    if re.search(r"runtime error: division by zero", error_message):
        return ErrorType.DIVISION_BY_ZERO
    if re.search(r"runtime error: load of value", error_message):
        return ErrorType.LOAD_OF_VALUE
    if re.search(r"runtime error:.+shift", error_message):
        return ErrorType.INVALID_SHIFT
    if re.search(r"runtime error: index.+out of bounds", error_message):
        return ErrorType.INDEX_OUT_OF_BOUNDS
    if re.search(r"runtime error:.+misaligned address", error_message):
        return ErrorType.MISALIGNED_ADDRESS
    if re.search(r"runtime error: signed integer overflow", error_message):
        return ErrorType.SIGNED_INTEGER_OVERFLOW

def find_ubsan_error(input_error: str):
    pattern_error = re.compile(r"(UndefinedBehaviorSanitizer:.*):")
    pattern = re.compile(r"UndefinedBehaviorSanitizer:.* (\w+\.\w+:\d+)")
    ubsan_error = []
    filepos = []
    for error in re.findall(pattern_error, input_error):
        ubsan_error.append(match_single_ubsan_error(error))
    for i in re.findall(pattern, input_error):
        filepos.append(i)
    ubsan_error_with_filepos = list(zip(ubsan_error, filepos))
    return ubsan_error_with_filepos

# returns [(Enum of Error, filename and line no as string)..]
def find_asan_errors(input_error: str):
    pt_error = re.compile(r"(AddressSanitizer:.*):")
    pattern = re.compile(r"AddressSanitizer:.*/(\w+\.\w+:\d+)")
    asan_error = []
    filepos = []
    for error in re.findall(pt_error, input_error):
        asan_error.append(match_single_asan_error(error))
    for i in re.findall(pattern, input_error):
        filepos.append(i)
    asan_error_with_filepos = list(zip(asan_error, filepos))
    return asan_error_with_filepos


def find_runtime_errors(input_error: str):
    pattern_file = re.compile(r"(\w+\.\w+:\d+).*:.runtime.error")
    pattern_runtime = re.compile(r"runtime.error.*")
    runtime_errors = []
    filepos = []
    for runtime_error in re.findall(pattern_runtime, input_error):
        runtime_errors.append(match_single_runtime_error(runtime_error))
    for i in re.findall(pattern_file, input_error):
        filepos.append(i)
    runtime_error_with_filepos = list(zip(runtime_errors, filepos))
    return runtime_error_with_filepos

def get_errors_with_filepos(input_error: str):
    return set(find_runtime_errors(input_error) + find_ubsan_error(input_error) + find_asan_errors(input_error))

def split_errors(error):
    return error.split("======")

if __name__ == '__main__':
    with open(os.path.join('error_logs', 'error_1.cng')) as f:
        with open(os.path.join('error_logs', 'error_0.cng')) as f1:
            file_str = f.read()
            file_str2 = f1.read()
            idk1 = get_errors_with_filepos(file_str)
            idk2 = get_errors_with_filepos(file_str2)
            print(idk1.symmetric_difference(idk2))
        # file_str = f.read()
        # idk = set(find_runtime_errors(file_str) + find_asan_errors(file_str) + find_ubsan_error(file_str))
        # print(idk)
        # print([e for e in [categorise_error(error) for error in split_errors(f.read())] if len(e) > 0])
