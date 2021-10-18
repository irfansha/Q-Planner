# Irfansha Shaik, 15.10.2021, Aarhus.

import subprocess
import os

class RunQute():

  def run_qute(self):
    if (self.dependency_learning == 1):
      command = self.solver_path + " --dependency-learning all --partial-certificate " + self.input_file_path + " > " + self.output_file_path
    else:
      command = self.solver_path + " --dependency-learning off --partial-certificate " + self.input_file_path + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")
    except subprocess.CalledProcessError as e:
      # 10, 20 are statuses for SAT and UNSAT:
      if ("exit status 10" not in str(e) and "exit status 20"  not in str(e)):
        print("Error from solver :", e, e.output)

  # parsing the qute solver output:
  def parse_qute_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Not needed as of now:
    #'''
    # Printing the data to the output for correctness purposes:
    for line in lines:
      if (line != '\n' and 'c' not in line):
        nline = line.strip("\n")
        print(nline)
    #'''

    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('UNSAT' in line):
        self.sat = 0
        return

    for line in lines:
      if ('SAT' in line):
        self.sat = 1
        break


    trimmed_line = lines[1].strip("\n")
    temp = trimmed_line.split(" ")
    for var in temp:
      if (var != '' and var != 'V'):
         if int(var) > 0:
           self.sol_map[int(var)] = 1
         else:
           self.sol_map[-int(var)] = 0

  def __init__(self, args):
    if (args.preprocessing == 0):
      self.input_file_path = args.encoding_out
    else:
      self.input_file_path = args.preprocessed_encoding_out
    self.dependency_learning = args.qute_dependency_learning
    self.output_file_path = args.solver_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'Qute', 'qute')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_qute()
    self.parse_qute_output()