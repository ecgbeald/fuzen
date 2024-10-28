import random, sys, hashlib

MIN_INT = -sys.maxsize - 1
MAX_INT = sys.maxsize

def generate(output_file, rng):
    cnf = ""
    if rng.random() < 0.25:
        # low both
        num_literals = rng.randint(1, 5) 
        num_clauses = rng.randint(1, 20)
    elif rng.random() < 0.5:
        # lots of clauses
        num_literals = rng.randint(1, 10) 
        num_clauses = rng.randint(1, 100)
    elif rng.random() < 0.75:
        # more literals
        num_literals = rng.randint(1, 100) 
        num_clauses = rng.randint(1, 80)
    else:
        # high both
        num_literals = rng.randint(1, 6000) 
        num_clauses = rng.randint(1, 8000)
    literals = []
    for _ in range(rng.randint(1, num_literals)):
        lit = str(rng.randint(1, max(50, num_literals - 2)))
        if rng.random() < 0.8:
            literals.append(lit)
            literals.append(f"-{lit}")
        elif rng.random() < 0.5:
            literals.append(lit)
        else:
            literals.append(f"-{lit}")

    literals_used = set()
    literals = list(set(literals))
    num_literals = len(literals)
    clauses_made = 0
    if rng.random() < 0.4:
        while len(literals_used) < len(literals):
            clause = ""
            rand = rng.random()
            if rand < 0.001:
                # empty clause
                pass
            elif rand < 0.95:
                # small clause
                for _ in range(rng.randint(2, 3)):
                    literal = rng.choice(literals)
                    clause += literal + " "
                    literals_used.add(literal)
            elif rand < 0.995:
                # normal clause
                for _ in range(rng.randint(0, 30)):
                    literal = rng.choice(literals)
                    clause += literal + " "
                    literals_used.add(literal)
            else:
                # big clause
                for _ in range(rng.randint(0, 200)):
                    literal = rng.choice(literals)
                    clause += literal + " "
                    literals_used.add(literal)
            clause += "0\n"
            cnf += clause
            clauses_made += 1
    else:
        for _ in range(num_clauses):
            clause = ""
            rand = rng.random()
            if rand < 0.01:
                # empty clause
                pass
            elif rand < 0.1:
                # small clause
                for _ in range(rng.randint(1, 5)):
                    clause += rng.choice(literals) + " "
            elif rand < 0.75:
                # normal clause
                for _ in range(rng.randint(1, 50)):
                    clause += rng.choice(literals) + " "
            else:
                # big clause
                for _ in range(rng.randint(1, 200)):
                    clause += rng.choice(literals) + " "
            clause += "0\n"
            cnf += clause
            clauses_made += 1

    header = "p cnf " + str(num_literals) + " " + str(clauses_made) + "\n"
    cnf = header + cnf

    with open(output_file, "w") as f:
        f.write(cnf)

def get_hash(cnf: str):
    return hashlib.md5(cnf.encode("utf-8")).hexdigest()

if __name__ == "__main__":
    rng = random.Random(1234)
    for i in range(10):
        generate("input.cnf", rng)
