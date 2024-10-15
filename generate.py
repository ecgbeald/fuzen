import random

def delete_random_character(input, seed = None):
    if len(input) == 1:
        return input
    random.seed(seed)
    index = random.randint(0, len(input)-1)
    return input[:index] + input[index+1:]

def add_random_number(input, seed = None):
    random.seed(seed)
    index = random.randint(0, len(input)-1)
    return input[:index] + str(random.randint(100000, 1000000) * random.choice([-1, 1])) + input[index:]

def duplicate_line(input, seed = None):
    random.seed(seed)
    lines = input.split('\n')
    line = lines[random.randint(0, len(lines)-1)]
    lines.insert(random.randint(0, len(lines)-1), line)
    return '\n'.join(lines)

def delete_random_word(input, seed = None):
    if len(input) == 1:
        return input
    random.seed(seed)
    index = random.randint(1, len(input)-1)
    if input[index] or input[index - 1] == '\n':
        return input
    return input[:index - 1] + input[index+1:]

def change_numbers(input):
    input.split('\n')
    index = random.randint(0, len(input)-1)
    return input[:index] + input[index+1:]

def mutate(input_file, seed = None):
    with open(input_file, "r") as f:
        input = f.read()

    random.seed(seed)
    iterations = random.randint(1, 4)
    output = input
    for i in range(iterations):
        output = random.choice([delete_random_word, duplicate_line, delete_random_character, add_random_number])(output, seed)

    with open(input_file, "w") as f:
        f.write(output)
