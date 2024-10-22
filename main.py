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

def delete_files(inputs = False, error_logs = False, input_logs = False):
    if inputs:
        for f in os.listdir():
            if f.startswith("input_") and f.endswith(".cnf"):
                os.remove(f)
    if error_logs:
        shutil.rmtree("error_logs")
    if input_logs:
        shutil.rmtree("input_logs")


def main(sut_path, input_path, seed, COVERAGE_LOCK, SAVED_ERRORS_LOCK):

    rng = random.Random(seed)

    thread_id = threading.get_ident()

    INPUT_FILE = f"input_{thread_id}.cnf"

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

    start_time = time.time()
    while True:
        input_id = f"{thread_id}_{idx}"
        errors = False
        
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

        with open(INPUT_FILE, "r") as f:
            cnf = f.read()
            if len(cnf) == 0:
                continue
            else:
                print(f"Input Hash: {get_hash(cnf)}")

        interesting = False

        try:
            COVERAGE_LOCK.acquire()
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

            coverage_interesting = False
            coverage, num_lines = get_coverage(sut_path)
        finally:
            COVERAGE_LOCK.release()
        
        new_coverage = update_coverage(coverage, num_lines, COVERAGE_LOCK) 

        if new_coverage:
            idx += 1
            SAVE_FILE = f"input_logs/input_{input_id}.cnf"
            # save input
            with open(SAVE_FILE, "w") as save_file:
                with open(INPUT_FILE, "r") as f:
                    save_file.write(f.read())
                    print(f"saved {f.read()[:10]} to {SAVE_FILE}")
            for i in range(MAX_MUTATIONS):
                to_mutate.append(SAVE_FILE)

        # need to change what is interesting
        if errors:
            with open("error.log", "r") as f:
                if len(f.read().strip()) == 0:
                    print("Error handled by SUT")
                    continue

            if not new_coverage:
                idx += 1
                # save input
                SAVE_FILE = f"input_logs/input_{input_id}.cnf"
                # save input
                with open(SAVE_FILE, "w") as save_file:
                    with open(INPUT_FILE, "r") as f:
                        print(f"saving {f.read()[:10]} to {SAVE_FILE}")
                        save_file.write(f.read())

            # save output
            with open("error.log", "r") as f:
                error = f.read()
                error_type = update_saved_errors(error, INPUT_FILE, SAVED_ERRORS_LOCK)
                print_saved_errors(SAVED_ERRORS_LOCK)
                print_unique_saved_errors(SAVED_ERRORS_LOCK)
                print("Unseen: " + "\n".join(unseen_errors(error)))
                if len(error_type) > 0:
                    with open(f"error_logs/error_{input_id}.cng", "w") as save_file:
                        save_file.write(error)

        idx += 1
        if time.time() - start_time > 10:
            break

        print()

    print_total_coverage_info(COVERAGE_LOCK)

if __name__ == "__main__":
    args = arg_parse()

    sut_path = args.SUT_PATH
    input_path = args.INPUT_PATH
    seed = args.SEED

    delete_files(
        inputs = True, 
        error_logs = True, 
        input_logs = True
    )

    Path('./error_logs').mkdir(parents=True, exist_ok=True)
    # keep 20 in here
    Path('./fuzzed-tests').mkdir(parents=True, exist_ok=True)
    Path('./input_logs').mkdir(parents=True, exist_ok=True)

    num_threads = 4

    SAVED_ERRORS_LOCK = threading.Lock()
    COVERAGE_LOCK = threading.Lock()

    threads: list[threading.Thread] = []
    for t_seed in range(seed, seed + num_threads):
        thread = threading.Thread(
            target=main, 
            args=(
                sut_path, 
                input_path, 
                t_seed, 
                SAVED_ERRORS_LOCK, 
                COVERAGE_LOCK
            )
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
