# Irfansha Shaik, 10.04.2021, Aarhus.

from utils.variables_dispatcher import VarDispatcher as vd

class SimpleEncoding:

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ') \n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ') \n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):
    # TODO: action and parameter variables
    # TODO: forall variables
    # TODO: static variables
    # TODO: non-static variables

    # Action and parameter variables are first existential layer:
    first_layer_variables = []
    self.quantifier_block.append(['# Action and parameter variables :'])
    for i in range(self.tfunc.parsed_instance.args.plan_length):
      self.quantifier_block.append(['# Time step 1 :'])
      self.quantifier_block.append(['# ' + str(self.action_variables[i])])
      self.quantifier_block.append(['# ' + str(self.parameter_variables[i])])
      first_layer_variables.extend(self.action_variables[i])
      for j in range(len(self.parameter_variables[i])):
        first_layer_variables.extend(self.parameter_variables[i][j])
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in first_layer_variables) + ')'])

    # Object variables are second forall layer:
    second_layer_variables = []
    self.quantifier_block.append(['# Forall object variables :'])
    self.quantifier_block.append(['# ' + str(self.forall_variables_list)])
    for i in range(len(self.forall_variables_list)):
      second_layer_variables.extend(self.forall_variables_list[i])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in second_layer_variables) + ')'])

    # Predicate variables are third existential layer:
    third_layer_variables = []

    self.quantifier_block.append(['# non-static predicate variables :'])
    self.quantifier_block.append(['# ' + str(self.static_variables)])
    third_layer_variables.extend(self.static_variables)
    self.quantifier_block.append(['# non-static predicate variables :'])
    for i in range(self.tfunc.parsed_instance.args.plan_length + 1):
      self.quantifier_block.append(['# ' + str(self.non_static_variables[i])])
      third_layer_variables.extend(self.non_static_variables[i])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in third_layer_variables) + ')'])


  def __init__(self, tfunc):
    self.tfunc = tfunc
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.final_output_gate = 0 # Can never be 0


    # Generating k sets of action and parameter variables:
    self.action_variables = []
    self.parameter_variables = []
    for i in range(tfunc.parsed_instance.args.plan_length):
      # Generating logarithmic action variables (along with noop):
      single_step_action_vars = self.encoding_variables.get_vars(tfunc.probleminfo.num_action_variables)
      self.action_variables.append(single_step_action_vars)
      # Generating logarithmic parameter variables for max parameter arity:
      single_step_parameter_variable_list = []
      for j in range(tfunc.probleminfo.max_action_parameters):
        step_parameter_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_parameter_variables)
        single_step_parameter_variable_list.append(step_parameter_variables)
      self.parameter_variables.append(single_step_parameter_variable_list)


    # generating forall varibles with max predicate arity:
    self.forall_variables_list = []
    for i in range(tfunc.probleminfo.max_predicate_parameters):
      # number of parameter variables is same as predicate parameters:
      step_forall_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_parameter_variables)
      self.forall_variables_list.append(step_forall_variables)


    # generating static variables only one set is enough, as no propagation:
    self.static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_static_predicates)

    # generating k+1 sets of non-static variables for propagation:
    self.non_static_variables = []
    for i in range(tfunc.parsed_instance.args.plan_length + 1):
      step_non_static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_non_static_predicates)
      self.non_static_variables.append(step_non_static_variables)


    self.generate_quantifier_blocks()

    # TODO: generate k copies of transition function
    # TODO: generate gates for initial state
    # TODO: generate gates for goal state
    # TODO: generate restricted constraints for forall varaibles based on types
