import random, string, sys, hashlib

MANUAL_INPUT = [ "p cnf 10 10\n",
                 "p cnf " + string.printable,
                 "p cnf 10 10\n" + string.printable,
                 "p cnf " + str(sys.maxsize + 1) + ' ' + str(sys.maxsize + 1) + '\n']

def delete_random_character(input_content, rng = random.Random()):
    if len(input_content) == 1:
        return input_content
    index = rng.randint(0, len(input_content)-1)
    return input_content[:index] + input_content[index+1:]

def add_random_number(input_content, rng = random.Random()):
    index = rng.randint(0, len(input_content) - 1)
    return input_content[:index] + str(rng.randint(100000, 1000000) * rng.choice([-1, 1])) + input_content[index:]

def duplicate_line(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    line = lines[rng.randint(0, len(lines)-1)]
    lines.insert(rng.randint(0, len(lines)-1), line)
    return '\n'.join(lines)

def delete_random_number(input_content, rng = random.Random()):
    if len(input_content) == 1:
        return input_content
    index = rng.randint(1, len(input_content) - 1)
    if input_content[index] or input_content[index - 1] == '\n':
        return input_content
    return input_content[:index - 1] + input_content[index + 1:]

def change_numbers(input_content):
    input_content.split('\n')
    index = rng.randint(0, len(input_content) - 1)
    return input_content[:index] + input_content[index + 1:]

def randomize_lines(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    rng.shuffle(lines)
    return '\n'.join(lines)

def add_trivial_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    lines.insert(rng.randint(0, len(lines)-1), "1 1 0")
    return '\n'.join(lines)

def add_infeasible_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    lines.insert(rng.randint(0, len(lines)-1), "1 1 0\n-1 -1 0")
    return '\n'.join(lines)

def duplicate_many_lines(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    line = lines[rng.randint(0, len(lines)-1)]
    lines.insert(rng.randint(0, len(lines)-1), line * 2000)
    return '\n'.join(lines)

def is_number(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
    
def flip_random_number(input_content, rng = random.Random()):
    numbers = input_content.split('\n')
    number = 0
    while not is_number(number) or number == 0:
        index = rng.randint(0, len(numbers) - 1)
        number = numbers[index]
    if "-" in number:
        return input_content[:index] + number[1:] + input_content[index+1:]
    else:
        return input_content[:index] + "-" + number + input_content[index+1:]

def add_long_clause(input_content, rng = random.Random()):
    line = ""
    for i in range(500):
        num = rng.randint(-100000, 100000)
        line += str(num) + ' '
    line += '0'
    return input_content + line

def mutate(input_file, rng = random.Random()):
    with open(input_file, "r") as f:
        input_content = f.read()

    iterations = rng.randint(1, 100)
    output = input_content
    for i in range(iterations):
        output = rng.choices(
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
                        )[0](output, rng)

    with open(input_file, "w") as f:
        f.write(output)

MIN_INT = -sys.maxsize - 1
MAX_INT = sys.maxsize

def generate(output_file, rng):
    cnf = ""
    num_literals = rng.randint(1, 25) * 2
    num_clauses = rng.randint(1, 25)
    literals = []
    for _ in range(rng.randint(1, num_literals // 2)):
        lit = str(rng.randint(1, 50))
        literals.append(lit)
        literals.append(f"-{lit}")

    for _ in range(num_clauses):
        clause = ""
        for _ in range(rng.randint(1, 10)):
            clause += rng.choice(literals) + " "
        clause += "0\n"
        cnf += clause

    header = "p cnf " + str(num_literals) + " " + str(num_clauses) + "\n"
    cnf = header + cnf

    # hash the cnf
    hash = hashlib.md5(cnf.encode("utf-8")).hexdigest()
    print(f"Input Hash: {hash}")

    with open(output_file, "w") as f:
        f.write(cnf)

if __name__ == "__main__":
    rng = random.Random(1234)
    for i in range(10):
        generate("input.cnf", rng)
