# Irfansha Shaik, 08.10.2021, Aarhus.

import subprocess
import os
from pysat.solvers import Cadical

class RunPedant():

  # TODO: Need to allow proof generation as well:
  def run_pedant(self):
    command = self.solver_path + " " + self.input_file_path + " --cnf " + self.certificate_out + " > " + self.output_file_path
    try:
      subprocess.run([command], shell = True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT ,check=True, timeout=self.time_limit)
    except subprocess.TimeoutExpired:
      self.timed_out = True
      print("Time out after " + str(self.time_limit)+ " seconds.")
    except subprocess.CalledProcessError as e:
      # 10, 20 are statuses for SAT and UNSAT:
      if ("exit status 10" not in str(e) and "exit status 20"  not in str(e)):
        print("Error from solver :", e, e.output)

  # parsing the pedant solver output:
  def parse_pedant_output(self):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()
    # Printing the data to the output for correctness purposes:
    for line in lines:
      #if (line != '\n'):
      if (line != '\n'):
        nline = line.strip("\n")
        print(nline)

    # Making sure the state of solution is explicitly specified:
    for line in lines:
      if ('UNSATISFIABLE' in line):
        self.sat = 0
        return

    for line in lines:
      if ('SATISFIABLE' in line):
        self.sat = 1
        break

  # parsing the caqe solver output:
  def parse_caqe_output(self, i, all_action_vars):
    f = open(self.output_file_path, 'r')
    lines = f.readlines()

    for line in lines:
      if ('V' in line):
        temp = line.split(" ")
        if (temp != ['\n']):
          literal = temp[1]
          if (int(literal) not in all_action_vars and -int(literal) not in all_action_vars):
            continue
          if int(literal) > 0:
            self.sol_map[i].append(int(literal))
          else:
            self.sol_map[i].append(int(literal))


  # If plan extraction is enabled, we extract the assignments:
  def parse_certificate_output(self, encoding):
    # we need each action variable and there dependencies i.e., the forall path variables:
    all_action_vars = []
    all_action_vars.extend(encoding.action_variables)
    for par_vars in encoding.parameter_variables:
      all_action_vars.extend(par_vars)


    # now parse through certificate and append models of all action variables:
    f = open(self.certificate_out, 'r')
    lines = f.readlines()
    f.close()

    header = lines.pop(0).strip("\n").split(" ")
    # we are adding more clauses equal to number of for all path variables:
    new_header = ''
    new_header = ' '.join(header[:-1])
    new_header += ( ' ' + str(int(header[-1]) + len(encoding.forall_path_variables)))

    # First initializing the solution map is each empty time step key:
    # For each forall path assignment, we need to find the corresponding value:
    for i in range(encoding.tfunc.parsed_instance.args.plan_length):
      binary_format = encoding.tfunc.generate_binary_format(encoding.forall_path_variables, i)
      self.sol_map[i] = []
      # we use the certificate output directly:
      f = open(self.certificate_out, 'w')
      f.write(new_header + '\n')
      for line in lines:
        f.write(line)
      for var in binary_format:
        f.write(str(var) + ' 0\n')
      f.close()

      command = self.extraction_solver_path + " --qdo " + self.certificate_out + " > " + self.output_file_path
      os.system(command)
      self.parse_caqe_output(i, all_action_vars)
    # Finally expand the solution map for the final action plan extraction:

  def __init__(self, encoding):
    args = encoding.tfunc.parsed_instance.args
    self.input_file_path = args.encoding_out
    self.output_file_path = args.solver_out
    self.certificate_out = args.certificate_out
    self.time_limit = args.time_limit
    # By default timeout not occured yet:
    self.timed_out = False
    self.solver_path = os.path.join(args.planner_path, 'solvers', 'pedant-solver', 'pedant')
    self.extraction_solver_path = os.path.join(args.planner_path, 'solvers', 'caqe', 'caqe')
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_pedant()
    self.parse_pedant_output()
    self.parse_certificate_output(encoding)
