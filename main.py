import os, subprocess, time, shutil, argparse
from pathlib import Path
from generate import mutate, MANUAL_INPUT
from parser import parse_error, ErrorType
from coverage import get_coverage

saved_errors = []

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("SUT_PATH", type=Path)
    parser.add_argument("INPUT_PATH", type=Path)
    parser.add_argument("SEED", type=int)
    return parser.parse_args()

# initialise array of 20
def init_saved_errors():
    for i in range(20):
        saved_errors.append((0, ErrorType.UNIDENTIFIED))

# update errors base on priority
def update_saved_errors(errortype, tmp_input_file):
    new_type = True
    current_types = [0] * ErrorType.ERROR_END.value[0]
    for i in range(20):
        saved_error_type = saved_errors[i][1].value[0]
        print(saved_error_type)
        current_types[saved_error_type] += 1
        if saved_error_type == errortype.value[0]:
            new_type = False
    print(new_type)

    new_priority = 0

    if new_type:
        new_priority = 5
    if errortype == ErrorType.UNIDENTIFIED:
        new_priority = 0

    min_priority = 999
    min_idx = -1
    for i in range(20):
        if saved_errors[i][0] < min_priority:
            min_priority = saved_errors[i][0]
            min_idx = i

    if min_priority != 999 and min_priority < new_priority:
        print(f"changing index", min_idx, "to priority", new_priority)
        saved_errors[min_idx] = (new_priority, errortype)
        # copy to the original file
        shutil.copy(tmp_input_file, f"fuzzed-tests/input_{min_idx}.cnf")
        print(saved_errors)
    else:
        print(f"unchanged")


# if __name__ == "__main__":
#     init_saved_errors()
#     for i in range(25):
#         update_saved_errors(ErrorType.SEGV, "input.cnf")
#     for i in range(25):
#         update_saved_errors(ErrorType.UNIDENTIFIED, "input.cnf")


if __name__ == "__main__":
    args = arg_parse()
    # in PosixPath, strips last slash
    sut_path = args.SUT_PATH
    input_path = args.INPUT_PATH
    seed = args.SEED

    Path('./error_logs').mkdir(parents=True, exist_ok=True)
    # keep 20 in here
    Path('./fuzzed-tests').mkdir(parents=True, exist_ok=True)
    Path('./input_logs').mkdir(parents=True, exist_ok=True)
    init_saved_errors()

    input_file = "input.cnf"

    filenames = [str(input_path) + f"/{f}" for f in os.listdir(input_path)]

    start_time = time.time()
    idx = 0
    best_coverage = {}

    while len(filenames) > 0:
        if idx < len(MANUAL_INPUT):
            with open(input_file, "w") as f:
                f.write(MANUAL_INPUT[idx])
            print(f"{idx}: {MANUAL_INPUT[idx]}")
        else:
            f_name = filenames.pop(0)
            shutil.copy(f_name, input_file)
            print(f"Processing {f_name}")

            # if not "inputs/" in f_name:
            # mutate(input_file)

            mutate(input_file, seed)

        with open(input_file, "r") as f:
            if len(f.read()) == 0:
                continue

        interesting = False

        with open("error.log", "w") as log_file:
            process = subprocess.Popen([f"{sut_path}/runsat.sh", input_file], stdout=subprocess.DEVNULL, stderr=log_file)
            try:
                return_code = process.wait(timeout=20)
                if return_code != 0:
                    print("Process returned non-zero exit code.")
                    interesting = True
            except subprocess.TimeoutExpired:
                process.terminate()
                print("Process timed out and was killed.")
                interesting = True
                log_file.write("Timeout\n")

        coverage = get_coverage(sut_path)
        for filename in coverage.keys():
            if filename in best_coverage:
                difference = set(coverage[filename]) - set(best_coverage[filename])
            else:
                best_coverage[filename] = coverage[filename]
                difference = set(coverage[filename])
            if difference:
                # new lines covered!
                print("new coverage", filename, difference)
                coverage_interesting = True
                best_coverage[filename].extend(list(difference))

        if interesting:
            with open("error.log", "r") as f:
                if len(f.read().strip()) == 0:
                    print("Error handled by SUT")
                    continue
            # save input

            with open(f"input_logs/input_{idx}.cnf", "w") as save_file:
                with open(input_file, "r") as f:
                    save_file.write(f.read())

            # add mutated input to queue
            filenames.append(f"input_logs/input_{idx}.cnf")

            # save output
            with open("error.log", "r") as f:
                error = f.read()
                # print(error)
                error_type = parse_error(error)
                print(f"Found error: {error_type}")
                update_saved_errors(error_type, input_file)
                with open(f"error_logs/error_{idx}.cng", "w") as save_file:
                    save_file.write(error)
                # print(f"Found error: {error_type}")
                # if error_type not in errors_seen:
                #     errors_seen.append(error_type)
                #
                #     with open(f"error_logs/error_{idx}.cnf", "w") as save_file:
                #         save_file.write(error)
                #
                # print(f"Errors seen: {errors_seen}")

            idx += 1

        if time.time() - start_time > 2000:
            break
