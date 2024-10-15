# there are cases where the asan would detect multiple errors
class ERROR:
    BUS = "BUS"
    SEGV = "SEGV"
    OVERFLOW = "heap-buffer-overflow"

def parse_error(error_message):
    if "AddressSanitizer:" in error_message:
        message = error_message.split("==ERROR:")[1]
        message = message.split("AddressSanitizer: ")[1]
        return message.split(" ")[0].strip()
    else:
        return error_message.strip()
