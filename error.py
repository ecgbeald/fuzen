import shutil
from parser import *

def unseen_errors(error_input):
    return [error for error in split_errors(error_input) if categorise_error(error) == set() and error.strip() != ""]

def update_saved_errors(error_input: str, tmp_input_file_location: str, SAVED_ERRORS, lock):
    current_type = categorise_error(error_input)
    if len(current_type) == 0:
        return set()
    segv_priority = 1
    heap_buffer_overflow_priority = 1
    current_priority = 0
    type_priority = 50
    error_pos = get_errors_with_filepos(error_input)
    for error in current_type:
        if error == ErrorType.SIG_SEGV:
            current_priority += segv_priority
        if error == heap_buffer_overflow_priority:
            current_priority += heap_buffer_overflow_priority
        else:
            current_priority += type_priority
    lowest_priority_idx = 21
    min_priority = 9999
    new_type = True
    already_stored = False

    try:
        lock.acquire()
        for i, (priority, stored_type, stored_error_pos) in enumerate(SAVED_ERRORS):
            if not stored_error_pos.symmetric_difference(error_pos):
                already_stored = True
                break
            if priority < min_priority:
                min_priority = priority
                lowest_priority_idx = i
            if not stored_type.symmetric_difference(current_type):
                new_type = False
        if already_stored:
            return set()
        if new_type:
            current_priority += 1000

        if current_priority > min_priority and lowest_priority_idx != 21:
            SAVED_ERRORS[lowest_priority_idx] = (current_priority, current_type, error_pos)
            shutil.copy(tmp_input_file_location, f"fuzzed-tests/input_{lowest_priority_idx}.cnf")
    finally:
        lock.release()

    return current_type

def print_saved_errors(SAVED_ERRORS, lock):
    try:
        lock.acquire()
        print("Saved errors: " + ", ".join([f"{p}: {s}" for p, s, _ in SAVED_ERRORS]) + "\n")
    finally:
        lock.release()

def print_unique_saved_errors(SAVED_ERRORS, lock):
    try:
        lock.acquire()
        print("Distinct errors found:\n> " + "\n> ".join(list(set([f"{s}" for p, ss, _ in SAVED_ERRORS for s in ss]))) + "\n")
    finally:
        lock.release()
