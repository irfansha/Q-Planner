# Irfansha Shaik, 07.10.2021, Linz.

from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as gg
from tarski.syntax import formulas as fr
import math
import utils.lessthen_cir as lsc


class LogEncoding:

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

    # forall object combination variables:
    all_forall_variables = []
    self.quantifier_block.append(['# Forall object variables :'])
    self.quantifier_block.append(['# ' + str(self.forall_variables_list)])
    for i in range(len(self.forall_variables_list)):
      all_forall_variables.extend(self.forall_variables_list[i])
    self.quantifier_block.append(['forall(' + ', '.join(str(x) for x in all_forall_variables) + ')'])

    # Inital, goal non-static predicate variables and static variables which only depend on object combination variables:
    all_outside_predicate_variables = []

    self.quantifier_block.append(['# initial non-static predicate variables :'])
    self.quantifier_block.append(['# ' + str(self.inital_non_static_variables)])
    all_outside_predicate_variables.extend(self.inital_non_static_variables)

    self.quantifier_block.append(['# goal non-static predicate variables :'])
    self.quantifier_block.append(['# ' + str(self.goal_non_static_variables)])
    all_outside_predicate_variables.extend(self.goal_non_static_variables)

    self.quantifier_block.append(['# static predicate variables :'])
    self.quantifier_block.append(['# ' + str(self.static_variables)])
    all_outside_predicate_variables.extend(self.static_variables)
    self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in all_outside_predicate_variables) + ')'])

    # All layers of non-static predicates:

    self.quantifier_block.append(['# non-static predicate variables and forall path variables:'])
    for i in range(self.plan_depth):
      self.quantifier_block.append(['# Layer ' + str(i) + ':'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.non_static_variables[3*i]) + ')'])
      self.quantifier_block.append(['forall(' + str(self.forall_path_variables[i]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.non_static_variables[3*i + 1]) + ')'])
      self.quantifier_block.append(['exists(' + ', '.join(str(x) for x in self.non_static_variables[3*i + 2]) + ')'])

    # action variables with only forall path variable dependencies:
    all_action_variables = []
    self.quantifier_block.append(['# Action and parameter variables :'])
    self.quantifier_block.append(['# ' + str(self.action_variables)])
    self.quantifier_block.append(['# ' + str(self.parameter_variables)])
    all_action_variables.extend(self.action_variables)
    for j in range(len(self.parameter_variables)):
      all_action_variables.extend(self.parameter_variables[j])

    # Specifying dependencies on forall path variables for action variables:
    for var in all_action_variables:
      dep_var_list = [var]
      dep_var_list.extend(self.forall_path_variables)
      self.quantifier_block.append(['depend(' + ', '.join(str(x) for x in dep_var_list) + ')'])


  # only one transition for DQBF:
  def generate_transition_function(self):
    # Generating transition function for each step:
    self.encoding.append(['# Transition funciton for step between last two predicate sets:'])
    # Generating auxilary vars:
    aux_vars = self.encoding_variables.get_vars(self.tfunc.num_auxilary_variables)
    # Appending transition output gates:
    self.transition_output_gate = aux_vars[-1]
    # Appending all variables required for one time step:
    all_vars = []
    all_vars.extend(self.action_variables)
    # Parameter variables:
    for j in range(len(self.parameter_variables)):
      all_vars.extend(self.parameter_variables[j])
    # Forall variables:
    for j in range(len(self.forall_variables_list)):
      all_vars.extend(self.forall_variables_list[j])
    # Static predicate variables:
    all_vars.extend(self.static_variables)
    # second last and last non-static predicates:
    all_vars.extend(self.non_static_variables[-2])
    all_vars.extend(self.non_static_variables[-1])
    # Auxilary variables:
    all_vars.extend(aux_vars)
    self.tfunc.new_transition_copy(all_vars, self.encoding)

  def generate_equality_clauses_between_layers(self):
    layer_equality_step_output_gates = []
    # Generating equality constraints for zero layer:
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Constraints in zero layer, connecting with start and end non-static predicate variables :'])
    self.encoding.append(['# Equality clause between P1 and START positons: '])
    self.gates_generator.complete_equality_gate(self.non_static_variables[1], self.inital_non_static_variables)
    temp_first_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# Equality clause between P2 and P0 non-static predicates: '])
    self.gates_generator.complete_equality_gate(self.non_static_variables[2], self.non_static_variables[0])
    temp_second_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if then for negative forall 0 variable and conjunction of two equality gates: '])
    self.gates_generator.if_then_gate(-self.forall_path_variables[0], [temp_first_equality_output_gate, temp_second_equality_output_gate])
    layer_equality_step_output_gates.append(self.gates_generator.output_gate)

    self.encoding.append(['# Equality clause between P1 and P0 non-static predicates: '])
    self.gates_generator.complete_equality_gate(self.non_static_variables[1], self.non_static_variables[0])
    temp_first_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# Equality clause between P2 and goal non-static predicates: '])
    self.gates_generator.complete_equality_gate(self.non_static_variables[2], self.goal_non_static_variables)
    temp_second_equality_output_gate = self.gates_generator.output_gate

    self.encoding.append(['# if then for positive forall 0 variable and conjunction of two equality gates: '])
    self.gates_generator.if_then_gate(self.forall_path_variables[0], [temp_first_equality_output_gate, temp_second_equality_output_gate])
    layer_equality_step_output_gates.append(self.gates_generator.output_gate)

    # For each layer until plan depth, generate equality clauses:
    for i in range(1,self.plan_depth):
      self.encoding.append(['# Constraints in ' + str(i) + 'th layer, connecting with start and end non-static predicates :'])
      self.encoding.append(['# Equality clause between P' + str(3*i) + ' and P' + str((3*i)+2) + ' non-static predicates: '])
      self.gates_generator.complete_equality_gate(self.non_static_variables[3*i], self.non_static_variables[(3*i) + 2])
      temp_first_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# Equality clause between P' + str((3*i)+1) + ' and P' + str((3*i)-2) + ' non-static predicates: '])
      self.gates_generator.complete_equality_gate(self.non_static_variables[(3*i)+1], self.non_static_variables[(3*i)-2])
      temp_second_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if then for negative forall ' + str(i) + ' variable and conjunction of two equality gates: '])
      self.gates_generator.if_then_gate(-self.forall_path_variables[i], [temp_first_equality_output_gate, temp_second_equality_output_gate])
      layer_equality_step_output_gates.append(self.gates_generator.output_gate)

      self.encoding.append(['# Equality clause between P' + str(3*i) + ' and P' + str((3*i)+1) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.non_static_variables[3*i], self.non_static_variables[(3*i) + 1])
      temp_first_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# Equality clause between P' + str((3*i)+2) + ' and P' + str((3*i)-1) + ' positons: '])
      self.gates_generator.complete_equality_gate(self.non_static_variables[(3*i)+2], self.non_static_variables[(3*i)-1])
      temp_second_equality_output_gate = self.gates_generator.output_gate

      self.encoding.append(['# if then for positive forall ' + str(i) + ' variable and conjunction of two equality gates: '])
      self.gates_generator.if_then_gate(self.forall_path_variables[i], [temp_first_equality_output_gate, temp_second_equality_output_gate])
      layer_equality_step_output_gates.append(self.gates_generator.output_gate)

    # Finally a conjunction of all the layer equalities:
    self.encoding.append(['# Final and gate for equality constraints: '])
    self.gates_generator.and_gate(layer_equality_step_output_gates)
    self.layer_equality_output_gate = self.gates_generator.output_gate

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
          obj_index = self.tfunc.probleminfo.object_names.index(subterm.name)
          gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
          self.gates_generator.and_gate(gate_variables)
          single_instance_gates.append(self.gates_generator.output_gate)
        self.gates_generator.and_gate(single_instance_gates)
        list_obj_instances.append(self.gates_generator.output_gate)
    # Finally an or gates for all the instances:
    self.gates_generator.or_gate(list_obj_instances)
    return self.gates_generator.output_gate

  def generate_initial_gate(self):
    initial_step_output_gates = []

    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Initial state: '])
    self.encoding.append(['# Type constraints: '])
    for valid_type_name in self.tfunc.parsed_instance.valid_type_names:
      # We consider only static predicate types:
      if valid_type_name not in self.tfunc.probleminfo.static_predicates:
        continue
      self.encoding.append(['# Type: ' + str(valid_type_name)])
      same_type_gates = []
      cur_type_objects = list(self.tfunc.parsed_instance.lang.get(valid_type_name).domain())
      for obj in cur_type_objects:
        # Since variables always have one parameter, we choose first set of forall variables:
        cur_variables = self.forall_variables_list[0]
        # Object index:
        obj_index = self.tfunc.probleminfo.object_names.index(obj.name)
        gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
        self.gates_generator.and_gate(gate_variables)
        same_type_gates.append(self.gates_generator.output_gate)

      # If any of the combination is true then, the predicate is true:
      self.gates_generator.or_gate(same_type_gates)
      type_final_gate = self.gates_generator.output_gate
      # Fetching corresponding static variable
      self.encoding.append(['# iff condition for the type predicate '])
      cur_static_variable = self.static_variables[self.tfunc.probleminfo.static_predicates.index(valid_type_name)]
      self.gates_generator.single_equality_gate(type_final_gate, cur_static_variable)
      initial_step_output_gates.append(self.gates_generator.output_gate)

    # Constraints for static variables that are not types:
    self.encoding.append(['# Non-type static predicate constraints: '])
    for static_predicate in self.tfunc.probleminfo.static_predicates:
      if static_predicate not in self.tfunc.parsed_instance.valid_type_names:
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
      # We look at the initial state, so we consider intial state non-state variables:
      cur_nonstatic_variable = self.inital_non_static_variables[self.tfunc.probleminfo.non_static_predicates.index(non_static_predicate)]
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
          obj_index = self.tfunc.probleminfo.object_names.index(subterm.name)
          gate_variables = self.tfunc.generate_binary_format(cur_variables, obj_index)
          self.gates_generator.and_gate(gate_variables)
          single_instance_gates.append(self.gates_generator.output_gate)
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
      # We look at the goal state, so corresponding non static variables:
      cur_nonstatic_variable = self.goal_non_static_variables[self.tfunc.probleminfo.non_static_predicates.index(non_static_predicate)]

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

  # Final output gate is an and-gate with inital, goal, transition, and layer equality gates:
  def generate_final_gate(self):
    final_gates_list = []
    final_gates_list.append(self.initial_output_gate)
    final_gates_list.append(self.goal_output_gate)
    final_gates_list.append(self.transition_output_gate)
    final_gates_list.append(self.layer_equality_output_gate)
    self.encoding.append(["# ------------------------------------------------------------------------"])
    self.encoding.append(['# Final output gate:'])
    self.encoding.append(['# And gate for initial, output, transition function gate and layer equality gate:'])
    self.gates_generator.and_gate(final_gates_list)
    self.final_output_gate = self.gates_generator.output_gate
    self.encoding.append(["# ------------------------------------------------------------------------"])

  def __init__(self, tfunc):
    self.tfunc = tfunc
    self.encoding_variables = vd()
    self.quantifier_block = []
    self.encoding = []
    self.initial_output_gate = 0 # initial output gate can never be 0
    self.goal_output_gate = 0 # goal output gate can never be 0
    self.transition_output_gate = 0 # can never be 0
    self.layer_equality_output_gate = 0 # can never be 0
    self.conditional_final_output_gate = 0 # Can never be 0
    self.final_output_gate = 0 # Can never be 0

    # Generating action and parameter variables:
    self.action_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_action_variables)
    # Generating logarithmic parameter variables for max parameter arity:
    self.parameter_variables = []
    for j in range(tfunc.probleminfo.max_action_parameters):
      step_parameter_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_parameter_variables)
      self.parameter_variables.append(step_parameter_variables)

    # generating forall varibles with max predicate arity:
    self.forall_variables_list = []
    for i in range(tfunc.probleminfo.max_predicate_parameters):
      # number of parameter variables is same as predicate parameters:
      step_forall_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_parameter_variables)
      self.forall_variables_list.append(step_forall_variables)


    # generating static variables only one set is enough, as no propagation:
    self.static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_static_predicates)

    # generating non-static variables for Initial and goal states:
    self.inital_non_static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_non_static_predicates)
    self.goal_non_static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_non_static_predicates)

    # for now we run plans of length 2 or more:
    assert(tfunc.parsed_instance.args.plan_length >= 2)
    # generating 3*log(depth) non-static variables for log propagation representation:
    self.plan_depth = math.ceil(math.log2(tfunc.parsed_instance.args.plan_length))
    self.non_static_variables = []
    for i in range(3*self.plan_depth):
      step_non_static_variables = self.encoding_variables.get_vars(tfunc.probleminfo.num_non_static_predicates)
      self.non_static_variables.append(step_non_static_variables)

    # forall path variables, representing layers:
    self.forall_path_variables = self.encoding_variables.get_vars(self.plan_depth)


    # Generating quantifer blocks:
    self.generate_quantifier_blocks()

    # A single transition function is enough between last two predicate sets:
    self.generate_transition_function()

    #print(self.transition_step_output_gates)

    self.gates_generator = gg(self.encoding_variables, self.encoding)

    # Generating equality clauses between different layers:
    self.generate_equality_clauses_between_layers()

    self.generate_initial_gate()

    self.generate_goal_gate()

    self.generate_final_gate()