# DIMACS fuzzer

DIMACS is a format describing a boolean formula in conjunctive normal form (CNF).
Some information about this format can be found at the following links:

- <https://fairmut3x.wordpress.com/2011/07/29/cnf-conjunctive-normal-form-dimacs-format-explained/>
- <http://www.domagoj-babic.com/uploads/ResearchProjects/Spear/dimacs-cnf.pdf>

The aim of the fuzzer is to find bugs in SAT solvers that were built in C.
The fuzzer will take as input one of these SAT solvers.

The interface of the resulting fuzzer is `fuzz-sat /path/to/SUT /path/to/inputs seed`.
