# Irfansha Shaik, 25.03.2021, Aarhus

'''
TODOS:
  1. Separate == from predicates and generate gates without forall variables.
  2. If an argument is either a constant or a parameter of type with one object,
     generate the fixed clause directly.
'''

import os
import argparse, textwrap
from parser import Parse as ps



# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("--path", help="path for domain and problem files", default = 'testcases/Blocks/')
  parser.add_argument("--domain", help="domain file path", default = 'domain.pddl')
  parser.add_argument("--problem", help="problem file path", default = 'prob01.pddl')
  parser.add_argument("--plan_out", help="plan output file path", default = 'cur_plan.txt')
  parser.add_argument("--plan_length", type=int,default = 4)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  UE = Ungrounded Encoding'''),default = 'UE')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan if found'''),default = 2)
  parser.add_argument("--VAL-testing", type=int, help="[0/1], default 0", default = 1)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'encoding')
  parser.add_argument("--solver", type=int, help=textwrap.dedent('''
                                       Solver:
                                       1 = caqe'''),default = 1)
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0",default = 0)
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-qdo (version 37)'''),default = 0)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()



  print(args)

  if args.version:
    print("Version 0.1")

  # Cannot extract a plan with simple bloqqer
  # (must use bloqqer-qdo instead):
  if (args.preprocessing == 1 and args.run == 2):
    print("ERROR: cannot extract plan with bloqqer, use bloqqer-qdo instead")
    exit()

  parsed_instance = ps(args)

  # Instead of action specific constraints,
  # predicate specific constraints are generated:
  parsed_instance.generate_predicate_constraints()