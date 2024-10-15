import os, subprocess, time, shutil, argparse
from pathlib import Path

from generate import mutate, MANUAL_INPUT
from parser import parse_error

errors_seen = []

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("SUT_PATH", type=Path)
    parser.add_argument("INPUT_PATH", type=Path)
    parser.add_argument("SEED", type=int)
    return parser.parse_args()

if __name__ == "__main__":
    args = arg_parse()
    # in PosixPath, strips last slash
    sut_path = args.SUT_PATH
    input_path = args.INPUT_PATH
    seed = args.SEED

    Path('./error_logs').mkdir(parents=True, exist_ok=True)
    # keep 20 in here
    Path('./fuzzed-tests').mkdir(parents=True, exist_ok=True)

    input_file = "input.cnf"

    filenames = [str(input_path) + f"/{f}" for f in os.listdir(input_path)]
    
    start_time = time.time()
    idx = 0

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

        if interesting:
            with open("error.log", "r") as f:
                if len(f.read().strip()) == 0:
                    print("Error handled by SUT")
                    continue
            # save input
            with open(f"fuzzed-tests/input_{idx}.cnf", "w") as save_file:
                with open(input_file, "r") as f:
                    save_file.write(f.read())
            
            # add mutated input to queue
            filenames.append(f"fuzzed-tests/input_{idx}.cnf")

            # save output
            with open("error.log", "r") as f:
                error = f.read()
                print(error)
                error_type = parse_error(error)
                print(f"Found error: {error_type}")
                if error_type not in errors_seen:
                    errors_seen.append(error_type)
                    
                    with open(f"error_logs/error_{idx}.cnf", "w") as save_file:
                        save_file.write(error)
                
                print(f"Errors seen: {errors_seen}")
                    
            idx += 1

        if time.time() - start_time > 2000:
            break
