# Irfansha Shaik, 05.04.2021, Aarhus.

import os
from parse.parser import Parse as ps

def test_blocks_domain(args):
  print("Testing Blocks domain:")
  # Setting args for Blocks domain:
  args.path = os.path.join(os.getcwd(), 'testing', 'testcases', 'Blocks')
  args.domain = 'domain.pddl'
  args.problem = 'prob01.pddl'
  args.debug = 0
  #print(args)
  parsed_instance = ps(args)

  # Instead of action specific constraints,
  # predicate specific constraints are generated:
  parsed_instance.generate_predicate_constraints()
  return 1