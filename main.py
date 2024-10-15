import os, subprocess, time, shutil, sys
from generate import mutate
from parser import ERROR, parse_error

errors_seen = []

if __name__ == "__main__":

    if len(sys.argv) > 2:
        sut_path = sys.argv[1]
        input_path = sys.argv[2]
    else:
        print("Usage: python3 main.py <sut_path> <input_path>")
        exit(1)

    input_file = "input.cnf"

    filenames = [f"inputs/{f}" for f in os.listdir(input_path)]
    
    start_time = time.time()
    id = 0
    while len(filenames) > 0:
        f_name = filenames.pop(0)
        shutil.copy(f_name, input_file)
        print(f"Processing {f_name}")

        # if not "inputs/" in f_name:
            # mutate(input_file)

        mutate(input_file, seed = 1234)

        with open(input_file, "r") as f:
            if len(f.read()) == 0:
                continue

        interesting = False

        with open("error.log", "w") as log_file:
            process = subprocess.Popen([sut_path, input_file], stdout=subprocess.DEVNULL, stderr=log_file)
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
            # save input
            with open(f"fuzzed-tests/input_{id}.cnf", "w") as save_file:
                with open(input_file, "r") as f:
                    save_file.write(f.read())
            
            # add mutated input to queue
            filenames.append(f"fuzzed-tests/input_{id}.cnf")

            # save output
            with open("error.log", "r") as f:
                error = f.read()
                print(error)
                error_type = parse_error(error)
                print(f"Found error: {error_type}")
                if error_type not in errors_seen:
                    errors_seen.append(error_type)
                    
                    with open(f"fuzzed-tests/output_{id}.cnf", "w") as save_file:
                        save_file.write(error)
                
                print(f"Errors seen: {errors_seen}")
                    
            id += 1

        if time.time() - start_time > 2000:
            break
