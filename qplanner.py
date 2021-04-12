# Irfansha Shaik, 25.03.2021, Aarhus

'''
TODOS:
  1. Separate == from predicates and generate gates without forall variables.
  2. If an argument is a constant generate the fixed clause directly.
  3. We add psuedo-grounded constraints for restricting search space for action variables
     based on psuedo-grounding of static-predicates.
  4. We also add constraints for forall variables based on predicate types to restrict search space.
'''

import os
import argparse, textwrap
from parse.parser import Parse as ps
import testing.tests as ts
import q_encodings.encoder as ge
from transition_function.simple_transition_function import SimpleTransitionFunction as stf
import run.run_solver as rs


# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("--path", help="path for domain and problem files", default = 'testing/testcases/Blocks/')
  parser.add_argument("--domain", help="domain file path", default = 'domain.pddl')
  parser.add_argument("--problem", help="problem file path", default = 'prob01.pddl')
  parser.add_argument("--plan_out", help="plan output file path", default = 'cur_plan.txt')
  parser.add_argument("--plan_length", type=int,default = 4)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  s-UE = Simple Ungrounded Encoding'''),default = 's-UE')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan if found'''),default = 2)
  parser.add_argument("--val_testing", type=int, help="[0/1], default 0", default = 1)
  parser.add_argument("--encoding_format", type=int, help="Encoding format: [1 = QCIR14 2 = QDIMACS], default 2",default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--solver", type=int, help=textwrap.dedent('''
                                       Solver:
                                       1 = quabs
                                       2 = caqe'''),default = 1)
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0",default = 0)
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-qdo (version 37)'''),default = 0)
  parser.add_argument("--time_limit", type=int, help="Solving time limit in seconds, default 900 seconds",default = 1800)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Preprocessing time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()



  print(args)

  if args.version:
    print("Version 0.2")

  # Cannot extract a plan with simple bloqqer
  # (must use bloqqer-qdo instead):
  if (args.preprocessing == 1 and args.run == 2):
    print("ERROR: cannot extract plan with bloqqer, use bloqqer-qdo instead")
    exit()

  # Run tests include all testcase domains:
  if (args.run_tests == 1):
    # We do not print any additional information:
    if (args.debug != 0):
      args.debug = 0
    ts.run_tests(args)
    exit()


  parsed_instance = ps(args)

  # Instead of action specific constraints,
  # predicate specific constraints are generated:
  parsed_instance.generate_predicate_constraints()

  # Generating simple transition function:
  tfunc = stf(parsed_instance)

  # Printing the transition function is debug is active:
  if (args.debug >= 1):
    print(tfunc)

  # TODO: Add new encoding generator module, and a new simple encoding module
  encoding = ge.generate_encoding(tfunc)
  # TODO: Add new strongly constrained encoding module

  if (args.run >= 1):
    rs.run_single_solver(encoding)