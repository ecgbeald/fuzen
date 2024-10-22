import random, string, sys, hashlib

MANUAL_INPUT = [ "p cnf 10 10\n",
                 "p cnf " + string.printable,
                 "p cnf 10 10\n" + string.printable,
                 "p cnf " + str(sys.maxsize + 1) + ' ' + str(sys.maxsize + 1) + '\n']

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
