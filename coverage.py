import subprocess, threading, os

COVERAGE = {}
NUM_LINES = {}

def process_coverage_file(filename):
    executed_lines = set()
    total_lines = 0

    with open(filename, 'r') as file:
        for line in file:
            parts = line.split(':') 
            if len(parts) > 2:
                exec_count = parts[0].strip()
                line_number = int(parts[1].strip()) 
                # if executable line, add to total count
                if exec_count != '-':   
                    total_lines += 1
                # if line was executed, add to executed lines
                if exec_count.isdigit() and int(exec_count) > 0:
                    executed_lines.add(line_number)
        
    return (executed_lines, total_lines)

def get_coverage(solver_path):
    solver_files = [f"{f.split('.gcno')[0]}" for f in os.listdir(solver_path) if f.endswith(".gcno")]
    executed = {}
    totals ={}
    # navigate to solver directory
    original_directory = os.getcwd()
    os.chdir(solver_path)
    for solver_file in solver_files:
        # run gcov on each file
        process = subprocess.Popen(["gcov", solver_file + ".gcno"], stdout=subprocess.DEVNULL)
        process.wait()
        # add coverage information to dictionaries
        lines, total = process_coverage_file(solver_file + ".c.gcov")
        executed[solver_file] = lines
        totals[solver_file] = total
        # delete data before next run
        if os.path.exists(solver_file + ".gcda"):
            os.remove(solver_file + ".gcda")
    # go back to original directory
    os.chdir(original_directory)
    return (executed, totals)

def print_coverage_info(executed, totals):
    print("\nCoverage information:\n")
    total_executed = 0
    total_lines = 0
    for key in executed.keys():
        # print percentage of lines executed for each file
        percent = len(executed[key])/totals[key] * 100
        print(f"{key}: {len(executed[key])}/{totals[key]} = {percent:.1f}%\n")
        # add to total count
        total_executed += len(executed[key])
        total_lines += totals[key]
    percent = total_executed / total_lines * 100
    print(f"Total coverage: {percent:.1f}%\n")

# Returns True if new coverage was added
def update_coverage(coverage, num_lines, lock):
    global COVERAGE, NUM_LINES
    try:
        lock.acquire()
        NUM_LINES = num_lines
        for filename in coverage.keys():
            if filename in COVERAGE:
                difference = coverage[filename] - COVERAGE[filename]
            else:
                COVERAGE[filename] = coverage[filename]
                difference = coverage[filename]
            if difference:
                print("New coverage:", filename, difference)
                COVERAGE[filename] = COVERAGE[filename].union(difference)
                return True
        return False
    finally:
        lock.release()

def print_total_coverage_info(lock):
    global COVERAGE, NUM_LINES
    try:
        lock.acquire()
        print_coverage_info(COVERAGE, NUM_LINES)
    finally:
        lock.release()
