# Irfansha Shaik, 25.03.2021, Aarhus

'''
TODOS:
  - New DQBF encoding for planning which is logarithmic in every aspect.
  - Ingore action costs and run the domains,seems to include many difficult domains that way.
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
import subprocess
import datetime


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
                                  s-UE = Simple Ungrounded Encoding (default)
                                  sc-UE = Strongly Constrained Ungrounded Encoding
                                  l-UE = Logarithmic Ungrounded Encoding (DQBF)'''),default = 's-UE')
  parser.add_argument("--run", type=int, help=textwrap.dedent('''
                               Three levels of execution:
                               0 = only generate encoding
                               1 = test plan existence
                               2 = extract the plan if found'''),default = 2)
  parser.add_argument("--val_testing", type=int, help="[0/1], default 1", default = 1)
  parser.add_argument("--encoding_format", help=textwrap.dedent('''
                                       Encoding format:
                                       [qcir/ qdimacs (default)/ dqcir/ dqdimacs'''),default = 'qdimacs')
  parser.add_argument("--encoding_out", help="output encoding file",default = 'intermediate_files/encoding')
  parser.add_argument("--intermediate_encoding_out", help="output intermediate encoding file",default = 'intermediate_files/intermediate_encoding')
  parser.add_argument("--solver", help=textwrap.dedent('''
                                       Solver:
                                       [quabs/ caqe (default)/ rareqs/ pedant/ qute]'''),default = 'caqe')
  parser.add_argument("--solver_out", help="solver output file",default = 'intermediate_files/solver_output')
  parser.add_argument("--certificate_out", help="output file for certificate (for DQBF pedant solver)",default = 'intermediate_files/certificate_output')
  parser.add_argument("--debug", type=int, help="[0/1], default 0" ,default = 0)
  parser.add_argument("--run_tests", type=int, help="[0/1], default 0",default = 0)
  parser.add_argument("--restricted_forall", type=int, help=" Additional clause to restrict forall branches [0/1/2], default 0",default = 0)
  parser.add_argument("--preprocessing", help=textwrap.dedent('''
                                       Preprocessing:
                                       [off (default)/ bloqqer/ bloqqer-qdo/ hqspre/ qratpre+'''),default = 'off')
  parser.add_argument("--internal_preprocessing", type=int, help="[0/1] If internal preprocessing available for a solver then enable it, default 1",default = 1)
  parser.add_argument("--preprocessed_encoding_out", help="output preprocessed encoding file",default = 'intermediate_files/preprocessed_encoding')
  parser.add_argument("--time_limit", type=float, help="Solving time limit in seconds, default 1800 seconds",default = 1800)
  parser.add_argument("--preprocessing_time_limit", type=int, help="Preprocessing time limit in seconds, default 900 seconds",default = 900)
  parser.add_argument("--qute_dependency_learning", type=int, help="[1/0] Enable/Disable dependency learning in Qute solver, default 0",default = 0)
  parser.add_argument("--invariants", type=int, help=textwrap.dedent('''
                               Four levels of invariants:
                               0 = none (default)
                               1 = inner most invariants (inside forall)
                               2 = operator invariants (outermost)
                               3 = both inner and outer invariants, default 0'''), default = 0)
  parser.add_argument("--invariants_out", help="output invariants file",default = 'intermediate_files/invariants')


  args = parser.parse_args()


  label = subprocess.check_output(["git", "describe", "--always"]).strip()


  print("Start time: " + str(datetime.datetime.now()))

  print("Git commit hash: " + str(label))

  print(args)

  if args.version:
    print("Version 0.6")

  # Cannot extract a plan with simple bloqqer
  # (must use bloqqer-qdo instead):
  if (args.preprocessing == 1 and args.run == 2 and args.solver == 'caqe'):
    print("ERROR: extract plan with bloqqer-qdo instead of bloqqer for CAQE")
    exit()

  # Cannot extract a plan with simple bloqqer (only plan existence available):
  if (args.preprocessing == 1 and args.run == 2):
    print("Warning: cannot extract plan with bloqqer, only plan existence")
    #exit()

  if (args.preprocessing == 3 and args.run == 2):
    print("Warning: cannot extract plan with HQSpre, only plan existence")
    #exit()

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
  if (args.e == 's-UE' or args.e == 'l-UE'):
    parsed_instance.generate_predicate_constraints()
    # Generating simple transition function:
    tfunc = stf(parsed_instance)
  elif (args.e == 'sc-UE'):
    parsed_instance.generate_only_nonstatic_predicate_constraints()
    tfunc = sctf(parsed_instance)

  # If the problem is trivially true, we exit:
  if (parsed_instance.already_solved == 1):
    print("Plan found")
    exit()

  # Printing the transition function is debug is active:
  if (args.debug >= 1):
    print(tfunc)

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


  print("Finish time: " + str(datetime.datetime.now()))