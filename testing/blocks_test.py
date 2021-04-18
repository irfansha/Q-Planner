# Irfansha Shaik, 05.04.2021, Aarhus.

import os
from parse.parser import Parse as ps

def test_blocks_domain(args):
  print("Testing Blocks domain:")
  # Setting args for Blocks domain:
  args.path = os.path.join(args.planner_path, 'testing', 'testcases', 'other' ,'Blocks')
  args.domain = 'domain.pddl'
  args.problem = 'prob01.pddl'
  args.debug = 0

  parsed_instance = ps(args)
  parsed_instance.generate_predicate_constraints()

  assert(len(parsed_instance.valid_types) == 2)
  assert(len(parsed_instance.valid_actions) == 4)
  return 1