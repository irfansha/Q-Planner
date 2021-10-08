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

    # First initializing the solution map is each empty time step key:
    for i in range(encoding.tfunc.parsed_instance.args.plan_length):
      self.sol_map[i] = []

    cur_var = 0
    step_model_clauses = []
    for line in lines:
      if ('c Model for variable' in line):
        # remembering the previous variable:
        prev_var = cur_var
        if (prev_var in all_action_vars):
          # We check for each time step within plan length:
          for i in range(encoding.tfunc.parsed_instance.args.plan_length):
            binary_format = encoding.tfunc.generate_binary_format(encoding.forall_path_variables, i)
            # for now just initializing solver again:
            c = Cadical()
            for clause in step_model_clauses:
              c.add_clause(clause)
            # Adding the forall path assginment:
            for each_forall_var  in binary_format:
              c.add_clause([each_forall_var])
            c.solve()
            model = c.get_model()
            if (prev_var in model):
              self.sol_map[i].append(prev_var)
            elif(-prev_var in model):
              self.sol_map[i].append(-prev_var)

        # Now a new variable model:
        cur_var = int(line.lstrip("c Model for variable ").rstrip(".\n"))
        step_model_clauses = []
      else:
        if (cur_var in all_action_vars):
          parsed_list = line.rstrip(" 0\n").split(" ")
          # We need integers list for the clauses:
          parsed_int_list = []
          for var in parsed_list:
            parsed_int_list.append(int(var))
          step_model_clauses.append(parsed_int_list)


    # For each forall path assignment, we need to find the corresponding value:
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
    self.sol_map = {}
    self.sat = -1 # by default plan not found.

    self.run_pedant()
    self.parse_pedant_output()
    self.parse_certificate_output(encoding)
