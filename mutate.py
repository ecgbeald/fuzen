import random
from string import punctuation, digits, ascii_lowercase

PROB_TO_CORRECT = 0.7

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
    if len(sections) < 4 or not is_number(sections[-1]):
        # not properly formatted, return original
        return header
    sections[-1] = str(int(sections[-1]) + num_to_add)
    return ' '.join(sections)

def change_literal_num(header, num_to_add):
    sections = header.split(' ')
    if len(sections) < 4 or not is_number(sections[-2]):
        # not properly formatted, return original
        return header
    sections[-2] = str(int(sections[-2]) + num_to_add)
    return ' '.join(sections)

def delete_random_character(input_content, rng = random.Random()):
    if len(input_content) == 1:
        return input_content
    index = rng.randint(0, max(1, len(input_content)-1))
    lines = input_content.split('\n')
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_literal_num(lines[0], -1)
    return input_content[:index] + input_content[index+1:]

def add_random_character(input_content, rng = random.Random()):
    if len(input_content) == 1:
        return input_content
    index = rng.randint(0, len(input_content)-1)
    lines = input_content.split('\n')
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_literal_num(lines[0], 1)
    return input_content[:index] + rng.choice(punctuation + digits + ascii_lowercase) +input_content[index+1:]

def add_random_number(input_content, rng = random.Random()):
    index = rng.randint(1, len(input_content) - 1)
    lines = input_content.split('\n')
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_literal_num(lines[0], 1)
    return input_content[:index] + str(rng.randint(-1000000, 1000000)) + input_content[index:]

def duplicate_line(input_content, rng = random.Random()):
    if rng.random() < 0.1:
        lines = input_content.split('\n')
        line = lines[rng.randint(0, len(lines)-1)]
        lines.insert(rng.randint(0, len(lines)-1), line)
        return '\n'.join(lines)
    else:
        lines = input_content.split('\n')
        if len(lines) < 2:
            return input_content
        line = lines[rng.randint(1, len(lines)-1)]
        lines.insert(rng.randint(1, len(lines)-1), line)
        # 50% chance adjust number of clauses to allow for clause removal
        if rng.random() < PROB_TO_CORRECT:
            lines[0] = change_clause_num(lines[0], 1)

        return '\n'.join(lines)

def delete_random_line(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    index = rng.randint(0, len(input_content) - 1)

    # 50% chance adjust number of clauses to allow for clause removal
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_clause_num(lines[0], -1)

    lines = lines[:index] + lines[index + 1:]

    return ' '.join(lines)

def randomize_lines(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    if rng.random() < 0.1:
        rng.shuffle(lines)
        return '\n'.join(lines)
    else:
        header = lines[0]
        clauses = lines [1:]
        rng.shuffle(clauses)
        return '\n'.join([header] + clauses)

def add_trivial_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    variable = get_random_variable(input_content, rng)
    lines.insert(rng.randint(0, len(lines)-1), f"{variable} {variable} 0")

    # 50% chance adjust number of clauses to allow for extra clause
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_clause_num(lines[0], 1)

    return '\n'.join(lines)

def add_infeasible_clause(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    variable = get_random_variable(input_content, rng)
    lines.insert(rng.randint(0, len(lines)-1), f"{variable} 0")
    lines.insert(rng.randint(0, len(lines)-1), f"-{variable} 0")

    # 50% chance adjust number of clauses to allow for extra clauses
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_clause_num(lines[0], 2)

    return '\n'.join(lines)

def add_similar_lines(input_content, rng = random.Random()):
    lines = input_content.split('\n')
    line = lines[rng.randint(0, len(lines)-1)]
    lines.insert(rng.randint(0, len(lines)-1), line)
    lines.insert(rng.randint(0, len(lines)-1), line + str(get_random_variable(input_content, rng)))
    lines.insert(rng.randint(0, len(lines)-1), line + f"-{str(get_random_variable(input_content, rng))}")
    lines.insert(rng.randint(0, len(lines)-1), line + str(get_random_variable(input_content, rng)))
    # 50% chance adjust number of clauses to allow for clause removal
    if rng.random() < PROB_TO_CORRECT:
        lines[0] = change_clause_num(lines[0], 3)

    return '\n'.join(lines)

def change_clauses(input_content, rng = random.Random()):
    lines = input_content.split('\n')

    lines[0] = change_clause_num(lines[0], rng.randint(-5, 5))

    return '\n'.join(lines)

def is_number(n):
    try:
        int(n)
        return True
    except ValueError:
        return False
    
def flip_random_number(input_content, rng = random.Random()):
    tokens = input_content.split(' ')
    for i in range(100):
        index = rng.randint(0, len(tokens) - 1)
        if not is_number(tokens[index]) and not is_number(tokens[index].removeprefix('-')):
            continue
        number = int(tokens[index].removeprefix('-'))
        number = -number if number < 0 else number
        tokens[index] = str(number)
        break
    return ' '.join(tokens)

def add_conflict(input_content, rng = random.Random()):
    tokens = input_content.split(' ')
    for i in range(100):
        index = rng.randint(0, len(tokens) - 1)
        if not is_number(tokens[index]) and not is_number(tokens[index].removeprefix('-')):
            continue
        number = int(tokens[index].removeprefix('-'))
        number = -number if number < 0 else number
        tokens.insert(index + 1, str(number))
        break
    return ' '.join(tokens)

def mutate(input_file, rng = random.Random(), iterations = 10):
    with open(input_file, "r") as f:
        input_content = f.read()

    if len(input_content) == 0:
        print("MUTATE: Empty file")
        return input_content
    print(iterations)
    iterations = rng.randint(1, iterations)
    output = input_content
    for i in range(iterations):
        func = rng.choice(
            [
                flip_random_number, 
                add_trivial_clause, 
                add_infeasible_clause, 
                randomize_lines,
                delete_random_line, 
                duplicate_line, 
                change_clauses, 
                delete_random_character, 
                add_random_character,
                add_conflict,
                add_similar_lines
            ]
        )
        print(func.__name__)
        output = func(output, rng)
        if len(output) == 0:
            output = input_content

    with open(input_file, "w") as f:
        f.write(output)
