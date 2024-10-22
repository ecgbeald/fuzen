import random

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

def change_numbers(input_content, rng = random.Random()):
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
    numbers = input_content.split(' ')
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
