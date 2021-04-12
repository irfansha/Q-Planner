# Irfansha Shaik, 12.04.2021, Aarhus.

class ExtractPlan():

  def extract_plan(self, encoding):
    for i in range(encoding.tfunc.parsed_instance.args.plan_length):
      # Extracting action name:
      action_name_string = ''
      for variable in encoding.action_variables[i]:
        action_name_string += str(self.sol_map[variable])
      # Action index, powers of two:
      action_index = int(action_name_string, 2)

      # If action index if equal to number of actions, then it is noop:
      if action_index == encoding.tfunc.probleminfo.num_valid_actions:
        action_name = 'noop'
      else:
        action_name = encoding.tfunc.probleminfo.valid_actions[action_index]
      object_list = []
      # Generating parameter variables based on arity of current action:
      cur_action = encoding.tfunc.parsed_instance.parsed_problem.get_action(action_name)
      for j in range(len(cur_action.parameters)):
        object_name_string = ''
        for single_parameter_variable in encoding.parameter_variables[i][j]:
          object_name_string += str(self.sol_map[single_parameter_variable])
        # Parameter object index, powers of two:
        object_index = int(object_name_string, 2)
        object_name = encoding.tfunc.probleminfo.objects[object_index]
        object_list.append(str(object_name))
      self.plan.append([action_name, tuple(object_list)])


  def print_plan(self):
    for action in self.plan:
      print(action)

  def print_updated_plan(self):
    for action in self.updated_format_plan:
      print(action)

  def print_to_file(self):
    f = open(self.file_path, 'w')
    for step_plan in self.updated_format_plan:
      f.write( step_plan + '\n')

  def update_format(self):
    count = 0
    for i in range(len(self.plan)):
      if (self.plan[i][0] != 'noop'):
        step_plan = self.plan[i]
        temp_string = str(count) + ': (' + step_plan[0] + ' '
        temp_list_string = ' '.join(list(step_plan[1]))
        self.updated_format_plan.append(temp_string + temp_list_string + ')')
        count += 1

  def __init__(self, encoding, sol_map):
    self.sol_map = sol_map
    self.file_path = encoding.tfunc.parsed_instance.args.plan_out
    self.plan = []
    self.updated_format_plan = []
    self.extract_plan(encoding)
    self.update_format()
    self.print_updated_plan()
    self.print_to_file()