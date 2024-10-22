import random, string, sys, hashlib

MANUAL_INPUT = [ "p cnf 10 10\n",
                 "p cnf " + string.printable,
                 "p cnf 10 10\n" + string.printable,
                 "p cnf " + str(sys.maxsize + 1) + ' ' + str(sys.maxsize + 1) + '\n']

def delete_random_character(input_content, seed = None):
    if len(input_content) == 1:
        return input_content
    index = random.randint(0, len(input_content)-1)
    return input_content[:index] + input_content[index+1:]

def add_random_number(input_content, seed = None):
    index = random.randint(0, len(input_content) - 1)
    return input_content[:index] + str(random.randint(100000, 1000000) * random.choice([-1, 1])) + input_content[index:]

def duplicate_line(input_content, seed = None):
    lines = input_content.split('\n')
    line = lines[random.randint(0, len(lines)-1)]
    lines.insert(random.randint(0, len(lines)-1), line)
    return '\n'.join(lines)

def delete_random_number(input_content, seed = None):
    if len(input_content) == 1:
        return input_content
    index = random.randint(1, len(input_content) - 1)
    if input_content[index] or input_content[index - 1] == '\n':
        return input_content
    return input_content[:index - 1] + input_content[index + 1:]

def change_numbers(input_content):
    input_content.split('\n')
    index = random.randint(0, len(input_content) - 1)
    return input_content[:index] + input_content[index + 1:]

def randomize_lines(input_content, seed = None):
    lines = input_content.split('\n')
    random.shuffle(lines)
    return '\n'.join(lines)

def add_trivial_clause(input_content, seed = None):
    lines = input_content.split('\n')
    lines.insert(random.randint(0, len(lines)-1), "1 1 0")
    return '\n'.join(lines)

def add_infeasible_clause(input_content, seed = None):
    lines = input_content.split('\n')
    lines.insert(random.randint(0, len(lines)-1), "1 1 0\n-1 -1 0")
    return '\n'.join(lines)

def duplicate_many_lines(input_content, seed = None):
    lines = input_content.split('\n')
    line = lines[random.randint(0, len(lines)-1)]
    lines.insert(random.randint(0, len(lines)-1), line * 2000)
    return '\n'.join(lines)

def is_number(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
    
def flip_random_number(input_content, seed = None):
    numbers = input_content.split('\n')
    number = 0
    while not is_number(number) or number == 0:
        index = random.randint(0, len(numbers) - 1)
        number = numbers[index]
    if "-" in number:
        return input_content[:index] + number[1:] + input_content[index+1:]
    else:
        return input_content[:index] + "-" + number + input_content[index+1:]

def add_long_clause(input_content, seed = None):
    line = ""
    for i in range(500):
        num = random.randint(-100000, 100000)
        line += str(num) + ' '
    line += '0'
    return input_content + line

def mutate(input_file, seed = None):
    with open(input_file, "r") as f:
        input_content = f.read()

    iterations = random.randint(1, 100)
    output = input_content
    for i in range(iterations):
        output = random.choices(
                        [
                            delete_random_number, duplicate_line, delete_random_character, randomize_lines, 
                            add_trivial_clause, add_infeasible_clause, duplicate_many_lines, flip_random_number, 
                            add_long_clause
                        ], 
                        weights = 
                        [
                            0.05, 0.1, 0.05, 0.1,
                            0.05, 0.2, 0.1, 0.05,
                            0.2
                        ],
                        k = 1
                        )[0](output, seed)

    with open(input_file, "w") as f:
        f.write(output)

MIN_INT = -sys.maxsize - 1
MAX_INT = sys.maxsize

def generate(output_file, seed = None):
    cnf = ""
    literals = list(set([
        random.choice([
            str(random.randint(1, 50)),
            chr(random.randint(97, 122))
        ]) for _ in range(random.randint(0, 50))
    ]))
    literals = literals + [f"-{l}" for l in literals]
    clauses = [
        " ".join([random.choice(literals) for _ in range(random.randint(0, 50))]) + " 0" for _ in range(random.randint(0, 50))
    ]
    header = "p cnf " + str(len(literals)) + " " + str(len(clauses)) + "\n"
    cnf = header + "\n".join(clauses)

    # hash the cnf
    hash = hashlib.md5(cnf.encode("utf-8")).hexdigest()
    print(f"Input Hash: {hash}")

    with open(output_file, "w") as f:
        f.write(cnf)

if __name__ == "__main__":
    generate("input.cnf")
