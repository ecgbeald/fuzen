import random, string, sys, hashlib

MANUAL_INPUT = [ "p cnf 10 10\n",
                 "p cnf " + string.printable,
                 "p cnf 10 10\n" + string.printable,
                 "p cnf " + str(sys.maxsize + 1) + ' ' + str(sys.maxsize + 1) + '\n']

def get_random_variable(input_content, rng = random.Random()):
    numbers = input_content.split(' ')
    number = 0
    index = rng.randint(0, len(numbers) - 1)
    while not is_number(number) or number == 0:
        index = rng.randint(0, len(numbers) - 1)
        number = numbers[index]
    if "-" in number:
        return number[1:]
    return number

def change_clause_num(header, num_to_add):
    sections = header.split(' ')
    if not is_number(sections[-1]):
        # not properly formatted, return original
        return header
    sections[-1] = str(int(sections[-1]) + num_to_add)
    return ' '.join(sections)

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

# def delete_random_number(input_content, rng = random.Random()):
#     if len(input_content) == 1:
#         return input_content
#     index = rng.randint(1, len(input_content) - 1)
#     if input_content[index] or input_content[index - 1] == '\n':
#         return input_content
#     return input_content[:index - 1] + input_content[index + 1:]

def delete_random_line(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    index = rng.randint(0, len(input_content) - 1)

    # 50% chance adjust number of clauses to allow for clause removal
    if random.random() < 0.5:
        lines[0] = change_clause_num(lines[0], -1)

    lines = lines[:index] + lines[index + 1:]

    return ' '.join(lines)

def randomize_lines(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    rng.shuffle(lines)
    return '\n'.join(lines)

def add_trivial_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    variable = get_random_variable(input_content, rng)
    lines.insert(rng.randint(0, len(lines)-1), f"{variable} {variable} 0")

    # 50% chance adjust number of clauses to allow for extra clause
    if random.random() < 0.5:
        lines[0] = change_clause_num(lines[0], 1)

    return '\n'.join(lines)

def add_infeasible_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    variable = get_random_variable(input_content, rng)
    lines.insert(rng.randint(0, len(lines)-1), f"{variable} 0")
    lines.insert(rng.randint(0, len(lines)-1), f"-{variable} 0")

    # 50% chance adjust number of clauses to allow for extra clauses
    if random.random() < 0.5:
        lines[0] = change_clause_num(lines[0], 2)

    return '\n'.join(lines)

# def duplicate_many_lines(input_content, rng = random.Random()):
#     lines = input_content.split('\n')
#     line = lines[rng.randint(0, len(lines)-1)]
#     lines.insert(rng.randint(0, len(lines)-1), line * 2000)
#     return '\n'.join(lines)

def is_number(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
    
def flip_random_number(input_content, rng = random.Random()):
    numbers = input_content.split(' ')
    number = 0
    index = rng.randint(0, len(numbers) - 1)
    while not is_number(number) or number == 0:
        index = rng.randint(0, len(numbers) - 1)
        number = numbers[index]
    if "-" in number:
        return ' '.join(numbers[:index]) + number[1:] + ' '.join(numbers[index+1:])
    else:
        return ' '.join(numbers[:index])  + "-" + number + ' '.join(numbers[index+1:])

# def add_long_clause(input_content, rng = random.Random()):
#     line = ""
#     for i in range(500):
#         num = rng.randint(-100000, 100000)
#         line += str(num) + ' '
#     line += '0'
#     return input_content + line

def mutate(input_file, rng = random.Random()):
    with open(input_file, "r") as f:
        input_content = f.read()

    iterations = rng.randint(1, 100)
    output = input_content
    for i in range(iterations):
        output = rng.choices(
                        [
                            flip_random_number, add_trivial_clause, add_infeasible_clause, randomize_lines,
                            delete_random_line
                            # delete_random_number, duplicate_line, delete_random_character, randomize_lines, 
                            # add_trivial_clause, add_infeasible_clause, duplicate_many_lines, 
                            # add_long_clause
                        ], 
                        # weights = 
                        # [
                        #     0.05, 0.1, 0.05, 0.1,
                        #     0.05, 0.2, 0.15,
                        #     0.2
                        # ],
                        k = 1
                        )[0](output, rng)

    with open(input_file, "w") as f:
        f.write(output)

MIN_INT = -sys.maxsize - 1
MAX_INT = sys.maxsize

def generate(output_file, rng):
    cnf = ""
    num_literals = rng.randint(1, 1000) * 2
    num_clauses = rng.randint(1, 1000)
    literals = []
    for _ in range(rng.randint(1, num_literals // 2)):
        lit = str(rng.randint(1, 50))
        literals.append(lit)
        literals.append(f"-{lit}")

    for _ in range(num_clauses):
        clause = ""
        for _ in range(rng.randint(1, 100)):
            clause += rng.choice(literals) + " "
        clause += "0\n"
        cnf += clause

    header = "p cnf " + str(num_literals) + " " + str(num_clauses) + "\n"
    cnf = header + cnf

    with open(output_file, "w") as f:
        f.write(cnf)

def get_hash(cnf: str):
    return hashlib.md5(cnf.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    rng = random.Random(1234)
    for i in range(10):
        generate("input.cnf", rng)
