# Irfansha Shaik, 30.04.2021, Aarhus.

from run.run_cpddl import RunCpddl as rc

class Invariants:

  def generate_invariant_constraints(tfunc):
    # TODO: run invariant generation tool
    # TODO: preprocess invariants to remove invalid (with invalid types) invariants
    # TODO: invariant constraints inside forall variables
    # TODO: invariant constraints for operator and parameter variables
    print("Generating invariant constraints, TODO")
    invariants = rc(tfunc)