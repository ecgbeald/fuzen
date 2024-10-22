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

    # idea: keep filenames here, maintain a new queue for mutation
    filenames = [str(input_path) + f"/{f}" for f in os.listdir(input_path)]
    # idea: keep files with more coverage in here so we can run mutation strategies based on generation list rather than the base filename list
    generation = []
    mutation = []
    # consider add a chance for mutation to be back in the filenames if it is really interesting
    MAX_MUTATIONS = 10
    MAX_ITERATIONS = 5

    iteration = 0
    gen = 0
    # idx is the test no
    idx = 0
    best_coverage = {}

    start_time = time.time()
    while True:

        print("Generation:", generation)

        if iteration >= MAX_ITERATIONS and len(generation) >= 3:
            gen += 1
            print("[#] Starting new Generation", gen)
            mutation = []
            filenames = generation

        if len(mutation) >= MAX_MUTATIONS:
            iteration += 1
            print("[#] Starting iteration", iteration)
            mutation = []

        # Generate an input
        generate(INPUT_FILE, rng)
        if rng.random() < 0.2:
            mutate(INPUT_FILE, rng)

        with open(INPUT_FILE, "r") as f:
            cnf = f.read()
            if len(cnf) == 0:
                continue
            else:
                print(f"Input Hash: {get_hash(cnf)}")

        interesting = False

        with open("error.log", "w") as log_file:
            process = subprocess.Popen([f"{sut_path}/runsat.sh", INPUT_FILE], stdout=subprocess.DEVNULL,
                                       stderr=log_file)
            try:
                return_code = process.wait(timeout=5)
                if return_code != 0:
                    print("Process returned non-zero exit code.")
                    interesting = True
            except subprocess.TimeoutExpired:
                process.terminate()
                print("Process timed out and was killed.")
                interesting = True
                log_file.write("Timeout\n")

        coverage_interesting = False
        coverage, num_lines = get_coverage(sut_path)
        for filename in coverage.keys():
            if filename in best_coverage:
                difference = coverage[filename] - best_coverage[filename]
            else:
                best_coverage[filename] = coverage[filename]
                difference = coverage[filename]
            if difference:
                # new lines covered!
                print("new coverage", filename, difference)
                coverage_interesting = True
                best_coverage[filename] = best_coverage[filename].union(difference)

        # need to change what is interesting
        if interesting and len(mutation) <= MAX_MUTATIONS:
            with open("error.log", "r") as f:
                if len(f.read().strip()) == 0:
                    print("Error handled by SUT")
                    continue
            # save input

            with open(f"input_logs/input_{idx}.cnf", "w") as save_file:
                with open(INPUT_FILE, "r") as f:
                    save_file.write(f.read())

            # add mutated input to queue
            mutation.append(f"input_logs/input_{idx}.cnf")
            if coverage_interesting:
                generation.append(f"input_logs/input_{idx}.cnf")

            # save output
            with open("error.log", "r") as f:
                error = f.read()
                # print(error)
                error_type = update_saved_errors(error, INPUT_FILE)
                print(saved_errors)
                print("\n".join(unseen_errors(error)))
                print("Distinct errors found: ", set([item for p, sublist in saved_errors for item in sublist]))
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

        idx += 1
        if time.time() - start_time > 200:
            break

        print()

    print_coverage_info(best_coverage, num_lines)
