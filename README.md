Instant Insanity consists of four cubes each of whose faces is one of four colors:

    https://en.wikipedia.org/wiki/Instant_Insanity

To map this problem to a quantum computer, we convert the puzzle into a set of eight
constraints.  Each of the eight constraints is mapped to a QUBO or Ising model, which
is minimized when the constraint is satisfied.  The sum of the eight constraints is
a QUBO or Ising model which represents the entire puzzle.  Minimizing this function
is equivalent to solving the puzzle.

This project relies on the Ocean SDK from D-Wave to build Ising models.  Additionally,
this project contains an implementation of the DEQO algorithm which is an alternate
way to generate QUBOs.

The top-level function subqubo_deqo.py invokes the DEQO algorithm for one of the eight
subQUBOs and writes the generated QUBO to a pickle file.  The top-level function
subqubo_ocean.py uses Ocean to generate an Ising model for one of the eight constraints
and writes its generated Ising model to a pickle file.