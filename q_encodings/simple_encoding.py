# Irfansha Shaik, 10.04.2021, Aarhus.

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as gg

class SimpleEncoding:

  def print_gate_tofile(self, gate, f):
    if len(gate) == 1:
      f.write(gate[0] + '\n')
    else:
      f.write(str(gate[1]) + ' = ' + gate[0] + '(' + ', '.join(str(x) for x in gate[2]) + ')\n')

  def print_encoding_tofile(self, file_path):
    f = open(file_path, 'w')
    for gate in self.quantifier_block:
      self.print_gate_tofile(gate, f)
    f.write('output(' + str(self.final_output_gate) + ')\n')
    for gate in self.encoding:
      self.print_gate_tofile(gate, f)

  # Generates quanifier blocks:
  def generate_quantifier_blocks(self):
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
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in third_layer_variables) + ')'])

  def generate_k_transitions(self):
    # Generating transition function for each step:
    for i in range(self.tfunc.parsed_instance.args.plan_length):
      self.encoding.append(['# Transition funciton for step ' + str(i) + ':'])
      # Generating auxilary vars:
      step_aux_vars = self.encoding_variables.get_vars(self.tfunc.num_auxilary_variables)
      # Appending transition output gates:
      self.transition_step_output_gates.append(step_aux_vars[-1])
      # Appending all variables required for one time step:
      all_vars = []
      all_vars.extend(self.action_variables[i])
      # Parameter variables:
      for j in range(len(self.parameter_variables[i])):
        all_vars.extend(self.parameter_variables[i][j])
      # Forall variables:
      for j in range(len(self.forall_variables_list)):
        all_vars.extend(self.forall_variables_list[j])
      # Static predicate variables:
      all_vars.extend(self.static_variables)
      # i, i+1 th non-static predicates:
      all_vars.extend(self.non_static_variables[i])
      all_vars.extend(self.non_static_variables[i+1])
      # Auxilary variables:
      all_vars.extend(step_aux_vars)
      self.tfunc.new_transition_copy(all_vars, self.encoding)

  # Finds object instantiations of a predicate and computes or-of-and gate:
  def generate_initial_predicate_constraints(self, predicate):
    list_obj_instances = []
    for atom in self.tfunc.parsed_instance.parsed_problem.init.as_atoms():
      if (atom.predicate.name == predicate):
        # Gates for one proposition:
        single_instance_gates = []
        # We generate and gates for each parameter:
        for i in range(len(atom.subterms)):
          subterm = atom.subterms[i]
          cur_variables = self.forall_variables_list[i]
          # Finding object index:
          for obj_index in range(len(self.tfunc.parsed_instance.lang.constants())):
            if (subterm.name == self.tfunc.parsed_instance.lang.constants()[obj_index].name):
              gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
              self.gates_generator.and_gate(gate_variables)
              single_instance_gates.append(self.gates_generator.output_gate)
              break
        self.gates_generator.and_gate(single_instance_gates)
        list_obj_instances.append(self.gates_generator.output_gate)
    # Finally an or gates for all the instances:
    self.gates_generator.or_gate(list_obj_instances)
    return self.gates_generator.output_gate

  # TODO: Testing is needed
  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])
    self.encoding.append(['# Type constraints: '])
    for valid_type in self.tfunc.parsed_instance.valid_types:
      # We consider only static predicate types:
      if valid_type.name not in self.tfunc.probleminfo.static_predicates:
        continue
      self.encoding.append(['# Type: ' + str(valid_type.name)])
      same_type_gates = []
      cur_type_objects = list(self.tfunc.parsed_instance.lang.get(valid_type.name).domain())
      for obj in cur_type_objects:
        # Since variables always have one parameter, we choose first set of forall variables:
        cur_variables = self.forall_variables_list[0]
        # Finding the position of object needed:
        for obj_index in range(len(self.tfunc.parsed_instance.lang.constants())):
          if (obj.name == self.tfunc.parsed_instance.lang.constants()[obj_index].name):
            gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
            self.gates_generator.and_gate(gate_variables)
            same_type_gates.append(self.gates_generator.output_gate)
            break
      # If any of the combination is true then, the predicate is true:
      self.gates_generator.or_gate(same_type_gates)
      type_final_gate = self.gates_generator.output_gate
      # Fetching corresponding static variable
      self.encoding.append(['# iff condition for the type predicate '])
      cur_static_variable = self.static_variables[self.tfunc.probleminfo.static_predicates.index(valid_type.name)]
      self.gates_generator.single_equality_gate(type_final_gate, cur_static_variable)
      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Constraints for static variables that are not types:
    self.encoding.append(['# Non-type static predicate constraints: '])
    for static_predicate in self.tfunc.probleminfo.static_predicates:
      type_flag = 0
      for valid_type in self.tfunc.parsed_instance.valid_types:
        if (valid_type.name == static_predicate):
          type_flag = 1
      # If not a type:
      if (type_flag == 0):
        self.encoding.append(['# static predicate: ' + str(static_predicate)])
        single_predicate_final_gate = self.generate_initial_predicate_constraints(static_predicate)
        # Fetching corresponding static variable
        self.encoding.append(['# iff condition for the predicate '])
        cur_static_variable = self.static_variables[self.tfunc.probleminfo.static_predicates.index(static_predicate)]
        self.gates_generator.single_equality_gate(single_predicate_final_gate, cur_static_variable)
        initial_step_output_gates.append(self.gates_generator.output_gate)

    # Constraints for non-static variables:
    self.encoding.append(['# Non-static predicate constraints: '])
    for non_static_predicate in self.tfunc.probleminfo.non_static_predicates:
      self.encoding.append(['# non-static predicate: ' + str(non_static_predicate)])
      single_predicate_final_gate = self.generate_initial_predicate_constraints(non_static_predicate)
      # Fetching corresponding non-static variable
      self.encoding.append(['# iff condition for the predicate '])
      # We look at the initial state, so 0th index predicates:
      cur_nonstatic_variable = self.non_static_variables[0][self.tfunc.probleminfo.non_static_predicates.index(non_static_predicate)]
      self.gates_generator.single_equality_gate(single_predicate_final_gate, cur_nonstatic_variable)
      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Final and gates of all constraints:
    self.encoding.append(['# Final inital output gate:'])
    self.gates_generator.and_gate(initial_step_output_gates)
    self.initial_output_gate = self.gates_generator.output_gate

  def __init__(self, tfunc):
    self.tfunc = tfunc
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
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

    # Generating quantifer blocks:
    self.generate_quantifier_blocks()
    # Generating k steps i.e., plan length number of transitions:
    self.generate_k_transitions()

    #print(self.transition_step_output_gates)

    self.gates_generator = gg(self.encoding_variables, self.encoding)

    # TODO: generate gates for initial state
    self.generate_initial_gate()
    # TODO: generate gates for goal state
    # TODO: generate restricted constraints for forall varaibles based on types
