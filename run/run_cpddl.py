# Irfansha Shaik, 30.04.2021, Aarhus

import os

class RunCpddl:

  def run(self):
    # Calling the tool
    os.system(self.cpddl_tool_path + ' -q ' + self.domain_path + ' ' + self.problem_path + ' > ' + self.invariants_out)

  def parse(self):
    f = open(self.invariants_out, 'r')
    lines = f.readlines()
    for line in lines:
      # We ignore the lines without any invariants:
      if ("{" in line and "}" in line):
        # Splitting at "{":
        split_lines = line.split("{")
        # removing trailing "}\n":
        cur_mutex_group = split_lines[-1].rstrip("}\n")
        # Splitting mutex group with ", ":
        split_invariants = cur_mutex_group.split(", ")
        cur_parsed_mutex_group = []
        for split_invariant in split_invariants:
          # further splitting each invaraints for arguments access:
          invariant_split_with_arguments = split_invariant.split(" ")
          # Other than the first element which is predicate name,
          # dividing rest of the arguments based on the types of invarints V, C or const:
          updated_invariant = [invariant_split_with_arguments[0]]
          for i in range(1, len(invariant_split_with_arguments)):
            cur_arg = invariant_split_with_arguments[i]
            # IF ':' is specified, then it is not constant:
            if (':' in cur_arg):
              split_cur_arg = cur_arg.split(":")
              # Using tuple to keep the structure intact:
              updated_invariant.append(tuple(split_cur_arg))
            else:
              # If constant, we explicitly specify it is const type:
              updated_invariant.append(('const', cur_arg))
          cur_parsed_mutex_group.append(updated_invariant)
        self.parsed_mutex_groups.append(cur_parsed_mutex_group)


  # Invariants with invalid parameter types are dropped:
  def filter_valid_invariants(self, tfunc):
    for mutex_group in self.parsed_mutex_groups:
      valid_single_mutex_group = []
      for single_invariant in mutex_group:
        valid_invariant_flag = 1
        # Checking if all the arguments in the invariant have valid type:
        for i in range(1, len(single_invariant)):
          # First element in the tuple gives the invariant type:
          cur_invariant_type = single_invariant[i][0]
          # Second element in the tuple gives the paramter type:
          cur_invariant_parameter_type = single_invariant[i][1]
          # We only need to filter general types, constants are fine:
          if (cur_invariant_type != 'const' and cur_invariant_parameter_type not in tfunc.parsed_instance.valid_type_names):
              # Making invariant invalid:
              valid_invariant_flag = 0
        if (valid_invariant_flag != 0):
          valid_single_mutex_group.append(single_invariant)
      # Dropping some invariants results in redundant invariants:
      if (valid_single_mutex_group not in self.valid_mutex_groups):
        self.valid_mutex_groups.append(valid_single_mutex_group)

  def __init__(self, tfunc):
    self.domain_path = os.path.join(tfunc.parsed_instance.args.path, tfunc.parsed_instance.args.domain)
    self.problem_path = os.path.join(tfunc.parsed_instance.args.path, tfunc.parsed_instance.args.problem)
    self.cpddl_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'cpddl' , 'pddl-lifted-mgroups')
    self.invariants_out = tfunc.parsed_instance.args.invariants_out
    self.parsed_mutex_groups = []
    self.valid_mutex_groups = []
    self.run()
    # TODO: Parse and update the invariants generated
    self.parse()
    # TODO: make it debug printing later:
    '''
    if (tfunc.parsed_instance.args.debug >= 1):
      for mutex_group in self.parsed_mutex_groups:
        print(mutex_group)
    '''
    #for mutex_group in self.parsed_mutex_groups:
    #  print(mutex_group)

    self.filter_valid_invariants(tfunc)

    for mutex_group in self.valid_mutex_groups:
      print(mutex_group)