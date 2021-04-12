# Irfansha Shaik, 12.04.2021, Aarhus

import os

# Calling val for testing:
def test_plan_with_val(args):
  val_path = os.path.join(os.getcwd(), 'tools', 'VAL', 'Validate')
  domain_path = os.path.join(args.path, args.domain)
  problem_path = os.path.join(args.path, args.problem)
  print("\nTesting with VAL: \n")
  command = val_path + ' ' + domain_path + ' ' + problem_path + ' ' + args.plan_out
  os.system(command)