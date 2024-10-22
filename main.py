import os, subprocess, time, argparse
from pathlib import Path
from mutate import *
from generate import *
from error import *
from coverage import *

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

    rng = random.Random(seed)

    Path('./error_logs').mkdir(parents=True, exist_ok=True)
    # keep 20 in here
    Path('./fuzzed-tests').mkdir(parents=True, exist_ok=True)
    Path('./input_logs').mkdir(parents=True, exist_ok=True)
    init_saved_errors()

    INPUT_FILE = "input.cnf"

    # idea: keep filenames here, maintain a new queue for to_mutate
    filenames = [str(input_path) + f"/{f}" for f in os.listdir(input_path)]
    # interesting files we want to mutate
    to_mutate = []
    # consider add a chance for to_mutate to be back in the filenames if it is reallyerrors
    MAX_MUTATIONS = 5

    iteration = 0
    gen = 0
    # idx is the test no
    idx = 0
    best_coverage = {}

    start_time = time.time()
    while True:
        print(idx)

        print("To mutate:", to_mutate)

        # If no inputs, generate an input
        if len(to_mutate) <= 0:
            INPUT_FILE = f"input_logs/input_{idx}.cnf"
            generate(INPUT_FILE, rng)
            # maybe mutate
            if rng.random() < 0.7:
                mutate(INPUT_FILE, rng)
        else:
            INPUT_FILE = to_mutate.pop(0)
            print("Mutating", INPUT_FILE)
            mutate(INPUT_FILE, rng)
        

        errors = False

        with open("error.log", "w") as log_file:
            process = subprocess.Popen([
                f"{sut_path}/runsat.sh", INPUT_FILE], 
                stdout=subprocess.DEVNULL,
                stderr=log_file
            )
            try:
                return_code = process.wait(timeout=10)
                if return_code != 0:
                    print("Process returned non-zero exit code.")
                    errors = True
                else:
                    print("Process returned zero exit code.")
            except subprocess.TimeoutExpired:
                process.terminate()
                print("Process timed out and was killed.")
                errors = True
                log_file.write("Timeout\n")

        # check for new coverage
        coverage, num_lines = get_coverage(sut_path)
        (new_coverage, best_coverage) = compare_coverage(best_coverage, coverage)
        if new_coverage:
            idx += 1
            SAVE_FILE = f"input_logs/input_{idx}.cnf"
            # save input
            with open(SAVE_FILE, "w") as save_file:
                with open(INPUT_FILE, "r") as f:
                    save_file.write(f.read())
                    print(f"saved {f.read()[:10]} to {SAVE_FILE}")
            for i in range(MAX_MUTATIONS):
                to_mutate.append(SAVE_FILE)

        if errors:
            # save error
            with open("error.log", "r") as f:
                if len(f.read().strip()) == 0:
                    print("Error handled by SUT")
                    continue

            if not new_coverage:
                idx += 1
                # save input
                SAVE_FILE = f"input_logs/input_{idx}.cnf"
                # save input
                with open(SAVE_FILE, "w") as save_file:
                    with open(INPUT_FILE, "r") as f:
                        print(f"saving {f.read()[:10]} to {SAVE_FILE}")
                        save_file.write(f.read())

            # add to saved errors
            with open("error.log", "r") as f:
                error = f.read()
                # print(error)
                error_type = update_saved_errors(error, INPUT_FILE)
                print(saved_errors)
                print("\n".join(unseen_errors(error)))
                print("===\nDistinct errors found:\n" + "\n".join(list(set([str(item) for p, sublist in saved_errors for item in sublist]))))
                if len(error_type) > 0:
                    with open(f"error_logs/error_{idx}.cng", "w") as save_file:
                        save_file.write(error)

                # print(f"Found error: {error_type}")
                # line1 = error.split('\n')[0] if len(error.split('\n')) > 0 else ""
                # line2 = error.split('\n')[1] if len(error.split('\n')) > 1 else ""
                # line3 = error.split('\n')[2] if len(error.split('\n')) > 2 else ""
                # if not ("SEGV" in line3 or "BUS" in line3 or "heap-buffer-overflow" in line2 or "Cannot apply remove_w_clause" in line1 or "Timeout" in line1):
                #     update_saved_errors(error_type, INPUT_FILE)
                #     with open(f"error_logs/error_{idx}.cng", "w") as save_file:
                #         save_file.write(error)

        if time.time() - start_time > 140:
            break

        print()

    print_coverage_info(best_coverage, num_lines)
