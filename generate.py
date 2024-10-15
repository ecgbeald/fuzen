import random
import string
import sys

MANUAL_INPUT = [ "p cnf 10 10\n",
                 "p cnf " + string.printable,
                 "p cnf 10 10\n" + string.printable,
                 "p cnf " + str(sys.maxsize + 1) + ' ' + str(sys.maxsize + 1) + '\n']

def delete_random_character(input_content, seed = None):
    if len(input_content) == 1:
        return input_content
    random.seed(seed)
    index = random.randint(0, len(input_content)-1)
    return input_content[:index] + input_content[index+1:]

def add_random_number(input_content, seed = None):
    random.seed(seed)
    index = random.randint(0, len(input_content) - 1)
    return input_content[:index] + str(random.randint(100000, 1000000) * random.choice([-1, 1])) + input_content[index:]

def duplicate_line(input_content, seed = None):
    random.seed(seed)
    lines = input_content.split('\n')
    line = lines[random.randint(0, len(lines)-1)]
    lines.insert(random.randint(0, len(lines)-1), line)
    return '\n'.join(lines)

def delete_random_word(input_content, seed = None):
    if len(input_content) == 1:
        return input_content
    random.seed(seed)
    index = random.randint(1, len(input_content) - 1)
    if input_content[index] or input_content[index - 1] == '\n':
        return input_content
    return input_content[:index - 1] + input_content[index + 1:]

def change_numbers(input_content):
    input_content.split('\n')
    index = random.randint(0, len(input_content) - 1)
    return input_content[:index] + input_content[index + 1:]

def randomize_lines(input_content, seed = None):
    random.seed(seed)
    lines = input_content.split('\n')
    random.shuffle(lines)
    return '\n'.join(lines)

def mutate(input_file, seed = None):
    with open(input_file, "r") as f:
        input_content = f.read()

    random.seed(seed)
    iterations = random.randint(1, 100)
    output = input_content
    for i in range(iterations):
        output = random.choice([delete_random_word, duplicate_line, delete_random_character, randomize_lines])(output, seed)

    with open(input_file, "w") as f:
        f.write(output)
