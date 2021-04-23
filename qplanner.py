# Irfansha Shaik, 25.03.2021, Aarhus

'''
TODOS:
  - Action parameter constraints dummy parameters can be added to simple transition function.
  - Not restricted to static-predicates, we can also add constraints from Initial and
    Goal states directly pruning away first and last actions.
  - Constraints between consecutive action steps can be added based on preconditions
    and effects something similar to mutex-op.
  - Seems direct mutex operators are available, need to check if useful.
  - Invariants seem useful (intuitively), can be added both at existence level and for universal layer.
  - Conditional constraints on forall vars seem to work, perhaps simpler constraints might work best.
  - Conditional effects might be perfect for our encoding, might be efficient than other approaches.
  - Ingore action costs and run the domains,seems to include many difficult domains that way.
  - We do not need k copies of non-static variables instead we can use the universal variables to
    "simulate" k steps with single transition function reducing encoding size -- worth investigating.
'''

import os
import time
import argparse, textwrap
from parse.parser import Parse as ps
import testing.tests as ts
import q_encodings.encoder as ge
from transition_function.simple_transition_function import SimpleTransitionFunction as stf
from transition_function.strongly_constrained_transition_function import StronglyConstrainedTransitionFunction as sctf
import run.run_solver as rs


# Main:
if __name__ == '__main__':
  text = "A tool to encode PDDL (strips) problems to SAT/QBF encodings and compute a plan if exists"
  parser = argparse.ArgumentParser(description=text,formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument("-V", "--version", help="show program version", action="store_true")
  parser.add_argument("--path", help="path for domain and problem files", default = 'testing/testcases/other/Blocks/')
  parser.add_argument("--domain", help="domain file path", default = 'domain.pddl')
  parser.add_argument("--problem", help="problem file path", default = 'prob01.pddl')
  parser.add_argument("--planner_path", help="path for qplanner.py, allowing remote run", default = os.getcwd())
  parser.add_argument("--plan_out", help="plan output file path", default = 'intermediate_files/cur_plan.txt')
  parser.add_argument("--plan_length", type=int,default = 4)
  parser.add_argument("-e", help=textwrap.dedent('''
                                  encoding types:
                                  s-UE = Simple Ungrounded Encoding
                                  sc-UE = Strongly Constrained Ungrounded Encoding'''),default = 's-UE')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan if found'''),default = 2)
  parser.add_argument("--val_testing", type=int, help="[0/1], default 1", default = 1)
  parser.add_argument("--encoding_format", type=int, help="Encoding format: [1 = QCIR14 2 = QDIMACS], default 2",default = 2)
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--intermediate_encoding_out", help="output intermediate encoding file",default = 'intermediate_files/intermediate_encoding')
  parser.add_argument("--solver", type=int, help=textwrap.dedent('''
                                       Solver:
                                       1 = quabs
                                       2 = CAQE
                                       3 = RaReQS'''),default = 2)
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0",default = 0)
  parser.add_argument("--restricted_forall", type=int, help=" Additional clause to restrict forall branches [0/1/2], default 0",default = 0)
  parser.add_argument("--preprocessing", type = int, help=textwrap.dedent('''
                                       Preprocessing:
                                       0 = off
                                       1 = bloqqer (version 37)
                                       2 = bloqqer-qdo (version 37)'''),default = 0)
  parser.add_argument("--preprocessed_encoding_out", help="output preprocessed encoding file",default = 'intermediate_files/preprocessed_encoding')
  parser.add_argument("--time_limit", type=float, help="Solving time limit in seconds, default 1800 seconds",default = 1800)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Preprocessing time limit in seconds, default 900 seconds",default = 900)
  args = parser.parse_args()



  print(args)

  if args.version:
    print("Version 0.5")

  # Cannot extract a plan with simple bloqqer
  # (must use bloqqer-qdo instead):
  if (args.preprocessing == 1 and args.run == 2 and args.solver == 2):
    print("ERROR: cannot extract plan with bloqqer, use bloqqer-qdo instead")
    exit()

  # Cannot extract a plan with simple bloqqer (only plan existence available):
  if (args.preprocessing == 1 and args.run == 2 and args.solver == 3):
    print("ERROR: cannot extract plan with bloqqer, only plan existence")
    exit()


  # Run tests include all testcase domains:
  if (args.run_tests == 1):
    # We do not print any additional information:
    if (args.debug != 0):
      args.debug = 0
    ts.run_tests(args)
    exit()

  # --------------------------------------- Timing the encoding ----------------------------------------
  start_encoding_time = time.perf_counter()

  parsed_instance = ps(args)

  # Instead of action specific constraints,
  # predicate specific constraints are generated:
  if (args.e == 's-UE'):
    parsed_instance.generate_predicate_constraints()
    # Generating simple transition function:
    tfunc = stf(parsed_instance)
  elif (args.e == 'sc-UE'):
    parsed_instance.generate_only_nonstatic_predicate_constraints()
    tfunc = sctf(parsed_instance)

  # If the problem is trivially true, we exit:
  if (parsed_instance.already_solved == 1):
    exit()

  # Printing the transition function is debug is active:
  if (args.debug >= 1):
    print(tfunc)

  # TODO: Add new encoding generator module, and a new simple encoding module
  encoding = ge.generate_encoding(tfunc)

  # TODO: Add new strongly constrained encoding module


  encoding_time = time.perf_counter() - start_encoding_time
  print("Encoding time: " + str(encoding_time))
  # ----------------------------------------------------------------------------------------------------

  if (args.run >= 1):
    # --------------------------------------- Timing the solver run ----------------------------------------
    start_run_time = time.perf_counter()

    rs.run_single_solver(encoding)

    solving_time = time.perf_counter() - start_run_time
    print("Solving time: " + str(solving_time) + "\n")
    # ------------------------------------------------------------------------------------------------------

  # ------------------------------------- Printing memory stats of encodings -----------------------------
  print("Encoding size (in KB): " + str(os.path.getsize(args.encoding_out)/1000))
  if (args.preprocessing == 1):
    print("Preprocessed encoding size (in KB): " + str(os.path.getsize(args.preprocessed_encoding_out)/1000))
  # ------------------------------------------------------------------------------------------------------