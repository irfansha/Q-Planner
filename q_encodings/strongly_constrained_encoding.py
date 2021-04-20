# Irfansha Shaik, 10.04.2021, Aarhus.

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as gg
from tarski.syntax import formulas as fr


# TODO: Update to adapt to strong constraints

'''
WARNING: It is possible that empty or gates might cause some problem,
not sure but better to check in testing
'''

class StronglyConstrainedEncoding:

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
      self.quantifier_block.append(['# Time step ' + str(i) + ' :'])
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
        self.encoding.append(['# Current atom constraint: ' + str(atom)])
        # Gates for one proposition:
        single_instance_gates = []
        # We generate and gates for each parameter:
        for i in range(len(atom.subterms)):
          subterm = atom.subterms[i]
          cur_variables = self.forall_variables_list[i]
          # Finding object index:
          for obj_index in range(len(self.tfunc.probleminfo.objects)):
            if (subterm.name == self.tfunc.probleminfo.objects[obj_index].name):
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

    # Constraints for static variables that are not types:
    self.encoding.append(['# Non-type static predicate constraints: '])
    for static_predicate in self.tfunc.probleminfo.static_predicates:
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

  # Finds object instantiations of a predicate and computes or-of-and gate:
  def generate_goal_predicate_constraints(self, predicate):
    # We generate gates for positive and negative clauses separately,
    pos_final_gate = 0
    neg_final_gate = 0
    zero_arity_predicate = 0

    list_obj_instances_pos = []
    list_obj_instances_neg = []
    if (fr.is_atom(self.tfunc.parsed_instance.parsed_problem.goal)):
      list_subformulas = [self.tfunc.parsed_instance.parsed_problem.goal]
    else:
      list_subformulas = self.tfunc.parsed_instance.parsed_problem.goal.subformulas
      assert(self.tfunc.parsed_instance.parsed_problem.goal.connective == fr.Connective.And)
    for atom in list_subformulas:
      # If it is negative atom, then we need to consider as
      # compund formula:
      if(fr.is_neg(atom)):
        # Asserting negation connective:
        assert(atom.connective == fr.Connective.Not)
        # Asserting single atom:
        assert(len(atom.subformulas) == 1)
        cur_atom = atom.subformulas[0]
      else:
        # If not negative, we do not change:
        cur_atom = atom
      if (cur_atom.predicate.name == predicate):
        # If it a zero arity predicate, then either positive or negative must
        # be present so returning directly if found:
        if (len(cur_atom.subterms) == 0):
          # again checking if positive or negative:
          if(fr.is_neg(atom)):
            zero_arity_predicate = -1
          else:
            zero_arity_predicate = 1
          # We do not look further:
          break
        # Gates for one proposition:
        single_instance_gates = []
        # We generate and gates for each parameter:
        for i in range(len(cur_atom.subterms)):
          subterm = cur_atom.subterms[i]
          cur_variables = self.forall_variables_list[i]
          # Finding object index:
          for obj_index in range(len(self.tfunc.probleminfo.objects)):
            if (subterm.name == self.tfunc.probleminfo.objects[obj_index].name):
              gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
              self.gates_generator.and_gate(gate_variables)
              single_instance_gates.append(self.gates_generator.output_gate)
              break
        # We only generate of some instantiation occurs:
        if (len(single_instance_gates) != 0):
          self.gates_generator.and_gate(single_instance_gates)
          # Appending to the right list:
          if (fr.is_neg(atom)):
            list_obj_instances_neg.append(self.gates_generator.output_gate)
          else:
            list_obj_instances_pos.append(self.gates_generator.output_gate)


    if (len(list_obj_instances_pos) != 0):
      # Finally an or gate for all the pos instances:
      self.encoding.append(['# Or gate for pos instances:'])
      self.gates_generator.or_gate(list_obj_instances_pos)
      pos_final_gate = self.gates_generator.output_gate
    if (len(list_obj_instances_neg) != 0):
      # Finally an or gates for all the neg instances:
      self.encoding.append(['# Or gate for neg instances:'])
      self.gates_generator.or_gate(list_obj_instances_neg)
      neg_final_gate = self.gates_generator.output_gate
    return [pos_final_gate, neg_final_gate, zero_arity_predicate]

  # Generating goal constraints:
  def generate_goal_gate(self):
    goal_step_output_gates = []
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Goal state: '])
    # Only non-static predicates are considered:
    # WARNING: we might be missig something, test here if something is wrong
    self.encoding.append(['# Non-static predicate constraints: '])
    for non_static_predicate in self.tfunc.probleminfo.non_static_predicates:
      self.encoding.append(['# non-static predicate: ' + str(non_static_predicate)])
      [pos_gate, neg_gate, zero_var] = self.generate_goal_predicate_constraints(non_static_predicate)

      # Fetching corresponding non-static variable
      # We look at the goal state, so plan length index predicates:
      cur_nonstatic_variable = self.non_static_variables[self.tfunc.parsed_instance.args.plan_length][self.tfunc.probleminfo.non_static_predicates.index(non_static_predicate)]

      if (pos_gate != 0):
        # positive if condition:
        self.encoding.append(['# if then condition for the pos predicate '])
        self.gates_generator.if_then_gate(pos_gate, cur_nonstatic_variable)
        goal_step_output_gates.append(self.gates_generator.output_gate)
      if (neg_gate != 0):
        # negative if condition:
        self.encoding.append(['# if then condition for the neg predicate '])
        self.gates_generator.if_then_gate(neg_gate, -cur_nonstatic_variable)
        goal_step_output_gates.append(self.gates_generator.output_gate)

      if (zero_var == 1):
        # if positive zero arity predicate condition:
        self.encoding.append(['# positive zero airty predicate '])
        goal_step_output_gates.append(cur_nonstatic_variable)
      if (zero_var == -1):
        # if negative zero arity predicate condition:
        self.encoding.append(['# negative zero airty predicate '])
        goal_step_output_gates.append(-cur_nonstatic_variable)


    # Final and gates of all constraints:
    self.encoding.append(['# Final goal output gate:'])
    self.gates_generator.and_gate(goal_step_output_gates)
    self.goal_output_gate = self.gates_generator.output_gate

  # TODO: We might be over-engineering, might work well for strongly constrained
  # transition function:
  def generate_restricted_forall_constraints(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Conditional forall constraints: '])

    # All conditional output gates:
    all_conditional_output_gates = []

    # Generating an object type index, where object type is the key
    # and all the object indexs of that types is the value list:
    obj_type_index = dict()

    # For each type we look at the set of objects with same type and add
    # it into out dictionary as indexes:
    for tp in self.tfunc.parsed_instance.lang.sorts:
      obj_list = list(self.tfunc.parsed_instance.lang.get(tp.name).domain())
      obj_index_list = []
      for obj in obj_list:
        for i in range(len(self.tfunc.probleminfo.objects)):
          if (obj.name == self.tfunc.probleminfo.objects[i].name):
            obj_index_list.append(i)
            break
      obj_index_list.sort()
      obj_type_index[tp] = obj_index_list

    # we do not want to iterate through again:
    local_valid_type_names_list = []
    # Since variables for types always have one parameter,
    # we choose first set of forall variables:
    cur_variables = self.forall_variables_list[0]
    # Constraint for types:
    for valid_type in self.tfunc.parsed_instance.valid_types:
      single_type_output_gates = []
      # We consider only static predicate types:
      local_valid_type_names_list.append(valid_type.name)
      # gathering all the types for or gate:
      cur_gates = []
      # if there are no objects, we ignore:
      if(len(obj_type_index[valid_type]) == 0):
        continue
      # Generating conditional clauses:
      self.encoding.append(['# Conditional for type ' + str(valid_type.name) + ': '])
      for valid_index in obj_type_index[valid_type]:
        gate_variables = self.tfunc.generate_binary_format(cur_variables, valid_index)
        self.gates_generator.and_gate(gate_variables)
        cur_gates.append(self.gates_generator.output_gate)
      self.encoding.append(['# Overall or gate for all possiblities: '])
      self.gates_generator.or_gate(cur_gates)
      single_type_output_gates.append(self.gates_generator.output_gate)
      # We need to restrict the other position forall variables for speed up:
      for i in range(1, self.tfunc.probleminfo.max_predicate_parameters):
        temp_forall_variables = self.forall_variables_list[i]
        # We go with first object by default, nothing special:
        self.encoding.append(['# restricted object clause: '])
        gate_variables = self.tfunc.generate_binary_format(temp_forall_variables, 0)
        self.gates_generator.and_gate(gate_variables)
        single_type_output_gates.append(self.gates_generator.output_gate)
      self.encoding.append(['# And gate for all parameters of single type: '])
      self.gates_generator.and_gate(single_type_output_gates)
      all_conditional_output_gates.append(self.gates_generator.output_gate)
    #print(all_conditional_output_gates)

    # Perhaps easier to just go through all the predicates at once:
    all_valid_predicates = []
    all_valid_predicates.extend(self.tfunc.probleminfo.static_predicates)
    all_valid_predicates.extend(self.tfunc.probleminfo.non_static_predicates)

    # Adding constraints for the forall variables based on predicates:
    for predicate in all_valid_predicates:
      if (predicate not in local_valid_type_names_list):
        self.encoding.append(['# Conditional for predicate ' + str(predicate) + ': '])
        cur_parameter_types = self.tfunc.parsed_instance.lang.get(predicate).sort
        single_predicate_output_gates = []
        for i in range(len(cur_parameter_types)):
          # depending on the position we fetch forall variables:
          cur_variables = self.forall_variables_list[i]
          cur_gates = []
          # generating or gate for all the possible objects of specified type:
          valid_objects_cur_type = obj_type_index[cur_parameter_types[i]]
          for valid_index in valid_objects_cur_type:
            gate_variables = self.tfunc.generate_binary_format(cur_variables, valid_index)
            self.gates_generator.and_gate(gate_variables)
            cur_gates.append(self.gates_generator.output_gate)
          self.encoding.append(['# Overall or gate for all possiblities for ' + str(i) + 'th parameter:'])
          self.gates_generator.or_gate(cur_gates)
          single_predicate_output_gates.append(self.gates_generator.output_gate)
        # We set rest of the parameters to 0 objects:
        for i in range(len(cur_parameter_types), self.tfunc.probleminfo.max_predicate_parameters):
          temp_forall_variables = self.forall_variables_list[i]
          # We go with first object by default, nothing special:
          self.encoding.append(['# restricted object clause: '])
          gate_variables = self.tfunc.generate_binary_format(temp_forall_variables, 0)
          self.gates_generator.and_gate(gate_variables)
          single_predicate_output_gates.append(self.gates_generator.output_gate)
        self.encoding.append(['# And gate for all parameter possibilities:'])
        self.gates_generator.and_gate(single_predicate_output_gates)
        all_conditional_output_gates.append(self.gates_generator.output_gate)


    self.encoding.append(['# Final conditional gate: '])
    self.gates_generator.or_gate(all_conditional_output_gates)
    self.conditional_final_output_gate = self.gates_generator.output_gate
    self.encoding.append(["# ------------------------------------------------------------------------"])

  def generate_simple_restricted_forall_constraints(self):

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Conditional forall constraints: '])

    # All conditional output gates:
    all_conditional_output_gates = []

    for cur_variables in self.forall_variables_list:
      for i in range(self.tfunc.probleminfo.num_objects, self.tfunc.probleminfo.num_possible_parameter_values):
        cur_invalid_forall_vars_list = self.tfunc.generate_binary_format(cur_variables, i)
        self.gates_generator.and_gate(cur_invalid_forall_vars_list)
        all_conditional_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# Final conditional gate: '])
    self.gates_generator.or_gate(all_conditional_output_gates)
    self.conditional_final_output_gate = -self.gates_generator.output_gate
    self.encoding.append(["# ------------------------------------------------------------------------"])


  # Final output gate is an and-gate with inital, goal and transition gates:
  def generate_final_gate(self):
    final_gates_list = []
    final_gates_list.append(self.initial_output_gate)
    final_gates_list.append(self.goal_output_gate)
    final_gates_list.extend(self.transition_step_output_gates)
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final output gate:'])
    self.encoding.append(['# And gate for initial, output and transition functions:'])
    self.gates_generator.and_gate(final_gates_list)
    # Restricting forall seems expensive, making it optional:
    if (self.tfunc.parsed_instance.args.restricted_forall >= 1):
      self.encoding.append(['# Conditional gate for forall restriction:'])
      self.gates_generator.if_then_gate(self.conditional_final_output_gate, self.gates_generator.output_gate)
    self.final_output_gate = self.gates_generator.output_gate
    self.encoding.append(["# ------------------------------------------------------------------------"])

  def __init__(self, tfunc):
    self.tfunc = tfunc
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_step_output_gates = []
    self.conditional_final_output_gate = 0 # Can never be 0
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

    self.generate_initial_gate()

    self.generate_goal_gate()

    # Restricting forall seems expensive, making it optional:
    if (self.tfunc.parsed_instance.args.restricted_forall == 1):
      self.generate_simple_restricted_forall_constraints()
    elif(self.tfunc.parsed_instance.args.restricted_forall == 2):
      self.generate_restricted_forall_constraints()

    self.generate_final_gate()