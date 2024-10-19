import subprocess
import os

def process_coverage_file(filename):
    executed_lines = []

    with open(filename, 'r') as file:
        for line in file:
            parts = line.split(':') 
            if len(parts) > 2:
                exec_count = parts[0].strip()
                line_number = int(parts[1].strip()) 
                
                if exec_count.isdigit() and int(exec_count) > 0:
                    executed_lines.append(line_number)
    return executed_lines

def get_coverage(solver_path):
    solver_files = [f"{f.split('.gcno')[0]}" for f in os.listdir(solver_path) if f.endswith(".gcno")]
    answer = {}
    # navigate to solver directory
    original_directory = os.getcwd()
    os.chdir(solver_path)
    for solver_file in solver_files:
        process = subprocess.Popen(["gcov", solver_file + ".gcno"], stdout=subprocess.DEVNULL)
        process.wait()
        lines = process_coverage_file(solver_file + ".c.gcov")
        answer[solver_file] = lines
    # go back to original directory
    os.chdir(original_directory)
    return answer
