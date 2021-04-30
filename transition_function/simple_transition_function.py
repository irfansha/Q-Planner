# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo
from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as gg
from constraints.invariants import Invariants as inv

class SimpleTransitionFunction:

  def map_generator(self):
    # Generating logarithmic action variables (along with noop):
    self.action_vars = self.transition_variables.get_vars(self.probleminfo.num_action_variables)
    # Generating logarithmic parameter variables for max parameter arity:
    self.parameter_variable_list = []
    for i in range(self.probleminfo.max_action_parameters):
      step_parameter_variables = self.transition_variables.get_vars(self.probleminfo.num_parameter_variables)
      self.parameter_variable_list.append(step_parameter_variables)

    # generating forall varibles with max predicate arity:
    self.forall_variables_list = []
    for i in range(self.probleminfo.max_predicate_parameters):
      # number of parameter variables is same as predicate parameters:
      step_forall_variables = self.transition_variables.get_vars(self.probleminfo.num_parameter_variables)
      self.forall_variables_list.append(step_forall_variables)

    # generating static variables only one set is enough, as no propagation:
    self.static_variables = self.transition_variables.get_vars(self.probleminfo.num_static_predicates)

    # generating two sets of non-static variables for propagation:
    self.first_non_static_variables = self.transition_variables.get_vars(self.probleminfo.num_non_static_predicates)
    self.second_non_static_variables = self.transition_variables.get_vars(self.probleminfo.num_non_static_predicates)

    # Adding action variables:
    for i in range(self.probleminfo.num_valid_actions):
      cur_action_variable_list = self.generate_binary_format(self.action_vars, i)
      self.variables_map[self.probleminfo.valid_actions[i]] = cur_action_variable_list

    # Adding action parameter variables:
    for action_name in self.probleminfo.valid_actions:
      action = self.parsed_instance.parsed_problem.get_action(action_name)
      # The key here is a tuple with action name and parameter symbol:
      for i in range(len(action.parameters)):
        self.variables_map[(action_name, action.parameters[i].symbol)] = self.parameter_variable_list[i]

    # Adding static variables to map:
    for i in range(len(self.probleminfo.static_predicates)):
      self.variables_map[self.probleminfo.static_predicates[i]] = self.static_variables[i]

    # Adding first-step non-static variables to map:
    for i in range(len(self.probleminfo.non_static_predicates)):
      self.variables_map[(self.probleminfo.non_static_predicates[i], 'first')] = self.first_non_static_variables[i]

    # Adding first-step non-static variables to map:
    for i in range(len(self.probleminfo.non_static_predicates)):
      self.variables_map[(self.probleminfo.non_static_predicates[i], 'second')] = self.second_non_static_variables[i]


  # Generates gate for single predicate constraint:
  def generate_single_gate(self, constraint):
    action_name = constraint[0]
    parameters = constraint[1]
    parameter_gates = []
    # Loop through each parameter and generate equality gates:
    for i in range(len(parameters)):
      parameter = parameters[i]
      forall_variables = self.forall_variables_list[i]
      # TODO: handle if a parameter is constant:
      if ('?' not in parameter):
        self.transition_gates.append(['# Generating binary constraint for constant parameter ' + str(parameter) + ':'])
        # Finding object position:
        for i in range(len(self.probleminfo.objects)):
          if (parameter == self.probleminfo.objects[i].name):
            constant_index = i
            break
        mapped_forall_variables = self.generate_binary_format(forall_variables, constant_index)
        self.gates_generator.and_gate(mapped_forall_variables)
      else:
        parameter_variables = self.variables_map[(action_name, parameter)]
        # Printing for redability:
        self.transition_gates.append(['# Equality gate for action parameter: (' + str(action_name) + ',' + str(parameter) + ') and ' + str(i) + 'th forall variables'])
        self.transition_gates.append(['# parameter vars : (' + ', '.join(str(x) for x in parameter_variables) + ')'])
        self.transition_gates.append(['# forall vars : (' + ', '.join(str(x) for x in forall_variables) + ')'])
        self.gates_generator.complete_equality_gate(parameter_variables, forall_variables)
      parameter_gates.append(self.gates_generator.output_gate)
    # Generating action name gate:
    self.transition_gates.append(['# And gate for action: ' + str(action_name)])
    self.gates_generator.and_gate(self.variables_map[action_name])
    action_name_gate = self.gates_generator.output_gate
    # Generating and gate for action name and all parameter gates:
    all_gates = []
    all_gates.extend(parameter_gates)
    all_gates.append(action_name_gate)
    parameter_gates.append(action_name_gate)

    self.gates_generator.and_gate(all_gates)
    return self.gates_generator.output_gate

  # Takes a list of constraints and generates gates generate single gate function:
  def constraints_generator(self, constraints, predicate_variable):
    condition_gates = []

    for constraint in constraints:
      output_gate = self.generate_single_gate(constraint)
      condition_gates.append(output_gate)
    # Only one of the action condition needs to be true:
    self.transition_gates.append(['# Or gate for condition action gates of the predicate'])
    self.gates_generator.or_gate(condition_gates)
    # For frame axiom we need the condition gate:
    if_condition_gate = self.gates_generator.output_gate
    # Generate if then gate for the predicate:
    self.transition_gates.append(['# If then gate for the predicate:'])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate, predicate_variable)
    return if_condition_gate


  # Takes a list of clause variables and maps to a integer value:
  def generate_binary_format(self, clause_variables, corresponding_number):
    num_variables = len(clause_variables)
    # Representation in binary requires number of variables:
    rep_string = '0' + str(num_variables) + 'b'
    bin_string = format(corresponding_number, rep_string)
    cur_variable_list = []
    # Depending on the binary string we set action variables to '+' or '-':
    for j in range(num_variables):
      if (bin_string[j] == '0'):
        cur_variable_list.append(-clause_variables[j])
      else:
        cur_variable_list.append(clause_variables[j])
    return cur_variable_list


  def generate_transition_function(self):
    self.gates_generator = gg(self.transition_variables, self.transition_gates)
    # For each type of condition i.e., pos_pre, neg_pre and so on, we gather the gates as and gate
    # We just gather gates for all predicates:
    predicate_final_gates = []

    # Generating gates for static predicates:
    for static_predicate in self.probleminfo.static_predicates:
      self.transition_gates.append(['# constraints for "' + str(static_predicate) + '" ----------------------------------------------'])
      # Looping through predicate constraints list for the current predicate:
      for single_predicate_constraints in self.parsed_instance.predicate_constraints:
        if (static_predicate == single_predicate_constraints.name):
          assert(len(single_predicate_constraints.pos_eff) == 0 and len(single_predicate_constraints.neg_eff) == 0)
          # Positive precondition constraints:
          self.transition_gates.append(['# Postive preconditions: '])
          if (len(single_predicate_constraints.pos_pre) != 0):
            self.constraints_generator(single_predicate_constraints.pos_pre, self.variables_map[static_predicate])
            predicate_final_gates.append(self.gates_generator.output_gate)
          # Negative precondition constraints:
          self.transition_gates.append(['# Negative preconditions: '])
          if (len(single_predicate_constraints.neg_pre) != 0):
            self.constraints_generator(single_predicate_constraints.neg_pre, -self.variables_map[static_predicate])
            predicate_final_gates.append(self.gates_generator.output_gate)
          break
      # Add seperator in encoding for better redability:
      self.transition_gates.append(["# ------------------------------------------------------------------------"])

    # Generating gates for non-static predicates:
    for non_static_predicate in self.probleminfo.non_static_predicates:
      self.transition_gates.append(['# constraints for "' + str(non_static_predicate) + '" ----------------------------------------------'])
      # Looping through predicate constraints list for the current predicate:
      for single_predicate_constraints in self.parsed_instance.predicate_constraints:
        if (non_static_predicate == single_predicate_constraints.name):
          # Positive precondition constraints:
          self.transition_gates.append(['# Postive preconditions: '])
          if (len(single_predicate_constraints.pos_pre) != 0):
            self.constraints_generator(single_predicate_constraints.pos_pre, self.variables_map[non_static_predicate, 'first'])
            predicate_final_gates.append(self.gates_generator.output_gate)
          # Negative precondition constraints:
          self.transition_gates.append(['# Negative preconditions: '])
          if (len(single_predicate_constraints.neg_pre) != 0):
            self.constraints_generator(single_predicate_constraints.neg_pre, -self.variables_map[non_static_predicate, 'first'])
            predicate_final_gates.append(self.gates_generator.output_gate)

          # We need effect gates for frame axiom constraints:
          effect_gates = []

          # Positive effect constraints:
          self.transition_gates.append(['# Postive effects: '])
          if (len(single_predicate_constraints.pos_eff) != 0):
            if_condition_gate = self.constraints_generator(single_predicate_constraints.pos_eff, self.variables_map[non_static_predicate, 'second'])
            effect_gates.append(if_condition_gate)
            predicate_final_gates.append(self.gates_generator.output_gate)
          # Negative effect constraints:
          self.transition_gates.append(['# Negative effects: '])
          if (len(single_predicate_constraints.neg_eff) != 0):
            if_condition_gate = self.constraints_generator(single_predicate_constraints.neg_eff, -self.variables_map[non_static_predicate, 'second'])
            effect_gates.append(if_condition_gate)
            predicate_final_gates.append(self.gates_generator.output_gate)

          assert(len(effect_gates) != 0)
          # Generating frame axiom, first non-static variable = second non-static variables OR or(effect_gates):
          self.transition_gates.append(['# Frame axiom equality gate: '])
          self.gates_generator.single_equality_gate(self.variables_map[non_static_predicate, 'first'], self.variables_map[non_static_predicate, 'second'])
          frame_gate = self.gates_generator.output_gate
          self.transition_gates.append(['# or gate for effect gate: '])
          self.gates_generator.or_gate(effect_gates)
          effect_or_gate = self.gates_generator.output_gate
          self.transition_gates.append(['# Frame axiom or gate: '])
          self.gates_generator.or_gate([frame_gate, effect_or_gate])
          # Adding frame axiom gate to the predicate final gates:
          predicate_final_gates.append(self.gates_generator.output_gate)
          break
      # Add seperator in encoding for better redability:
      self.transition_gates.append(["# ------------------------------------------------------------------------"])

    invalid_action_gates = []
    # Generating negative constraints for impossible actions, ignore noop action:
    self.transition_gates.append(['# Invalid action gates: '])
    for i in range(self.probleminfo.num_valid_actions + 1, self.probleminfo.num_possible_actions):
      cur_invalid_action_vars_list = self.generate_binary_format(self.action_vars, i)
      self.gates_generator.and_gate(cur_invalid_action_vars_list)
      invalid_action_gates.append(self.gates_generator.output_gate)

    # Or gate to check if any one of them is true:
    if (len(invalid_action_gates) != 0):
      self.gates_generator.or_gate(invalid_action_gates)
      self.invalid_actions_final_gate = self.gates_generator.output_gate
      # Adding negative of invalid or gates:
      predicate_final_gates.append(-self.invalid_actions_final_gate)

    invalid_parameter_gates = []
    # Generating negative constraints for impossible parameter values:
    self.transition_gates.append(['# Invalid parameter gates: '])
    for parameter_vars in self.parameter_variable_list:
      for i in range(self.probleminfo.num_objects, self.probleminfo.num_possible_parameter_values):
        cur_invalid_parameter_vars_list = self.generate_binary_format(parameter_vars, i)
        self.gates_generator.and_gate(cur_invalid_parameter_vars_list)
        invalid_parameter_gates.append(self.gates_generator.output_gate)

    # Or gate to check if any one of them is true:
    if (len(invalid_parameter_gates) != 0):
      self.gates_generator.or_gate(invalid_parameter_gates)
      self.invalid_parameters_final_gate = self.gates_generator.output_gate
      # Adding negative of invalid or gates:
      predicate_final_gates.append(-self.invalid_parameters_final_gate)


    equality_output_gates = []
    # TODO: testing needed
    # we do not handle constants yet, to be handled:
    for single_predicate_constraints in self.parsed_instance.predicate_constraints:
      if (single_predicate_constraints.name == '='):
        self.transition_gates.append(["# ------------------------------------------------------------------------"])
        self.transition_gates.append(['# Equality gates: '])
        # Asserting positive equality constraints not available:
        assert(len(single_predicate_constraints.pos_pre) == 0)
        for constraint  in single_predicate_constraints.neg_pre:
          action_name = constraint[0]
          cur_action_vars = self.variables_map[action_name]
          self.transition_gates.append(['# Action and equality parameters gates: ' + str(constraint)])
          self.gates_generator.and_gate(cur_action_vars)
          cur_action_gate = self.gates_generator.output_gate
          # equality constraints have arity 2:
          first_parameter = constraint[1][0]
          second_parameter = constraint[1][1]
          # If a parameter is constant we get the binary representation list:
          if ('?' not in first_parameter and '?' in second_parameter):
            first_parameter_variables = []
            second_parameter_variables = self.variables_map[(action_name, second_parameter)]
            self.transition_gates.append(['# Generating binary constraint for second parameter because of first constant parameter:'])
            # Finding object position:
            for i in range(len(self.probleminfo.objects)):
              if (first_parameter == self.probleminfo.objects[i].name):
                constant_index = i
                break
            formatted_parameter_variables = self.generate_binary_format(second_parameter_variables, constant_index)
            self.gates_generator.and_gate(formatted_parameter_variables)
          elif ('?' in first_parameter and '?' not in second_parameter):
            first_parameter_variables = self.variables_map[(action_name, first_parameter)]
            second_parameter_variables = []
            self.transition_gates.append(['# Generating binary constraint for first parameter because of second constant parameter:'])
            # Finding object position:
            for i in range(len(self.probleminfo.objects)):
              if (second_parameter == self.probleminfo.objects[i].name):
                constant_index = i
                break
            formatted_parameter_variables = self.generate_binary_format(first_parameter_variables, constant_index)
            self.gates_generator.and_gate(formatted_parameter_variables)
          elif('?' in first_parameter and '?' in second_parameter):
            first_parameter_variables = self.variables_map[(action_name, first_parameter)]
            second_parameter_variables = self.variables_map[(action_name, second_parameter)]
            self.transition_gates.append(['# Generating equality constraints:'])
            self.gates_generator.complete_equality_gate(first_parameter_variables, second_parameter_variables)
          # We assert that both parameters are not constant:
          assert('?' in first_parameter or '?' in second_parameter)
          # Regardless of which branch taken we take the output gate:
          output_gate = self.gates_generator.output_gate
          # both are mutually exclusive:
          self.gates_generator.if_then_gate(cur_action_gate, -output_gate)
          equality_output_gates.append(self.gates_generator.output_gate)
        self.transition_gates.append(["# ------------------------------------------------------------------------"])
        break

    if (len(equality_output_gates) != 0):
      self.transition_gates.append(['# Final Equality output gate: '])
      self.gates_generator.and_gate(equality_output_gates)
      predicate_final_gates.append(self.gates_generator.output_gate)
      self.transition_gates.append(["# ------------------------------------------------------------------------"])

    # For now only generating inner most invariants when given option 1:
    if (self.parsed_instance.args.invariants == 1):
      print("Adding invariant constraints")
      inv.generate_invariant_constraints(self)

    # Generating 'and' gate for all predicate condition gates:
    self.transition_gates.append(['# Final predicate condition "and" gate: '])
    self.gates_generator.and_gate(predicate_final_gates)
    self.final_transition_gate = self.gates_generator.output_gate

  def __init__(self, parsed_instance):
    self.probleminfo = pinfo(parsed_instance)
    self.parsed_instance = parsed_instance
    self.variables_map = dict()
    self.string_variables_map = ''
    self.transition_gates = []
    self.final_transition_gate = 0 # Never be zero
    self.main_variables = 0 # Never be zero
    self.num_auxilary_variables = 0 # Never be zero

    if (self.parsed_instance.args.debug >= 1):
      print(self.probleminfo)
    # Using variable dispatcher for new integer variables:
    self.transition_variables = vd()

    # Mapping variables to integer variables for encoding:
    self.map_generator()
    self.string_variables_map = "   {" + "\n    ".join("{!r}: {!r},".format(k, v) for k, v in self.variables_map.items()) + "}"

    # Specifying the number of main variables,
    # next var -1 is the current var:
    self.num_main_variables = self.transition_variables.next_var - 1

    # Generating transition function:
    self.generate_transition_function()
    self.string_transition_gates = ''
    #for gate in self.transition_gates:
    #    self.string_transition_gates += str(gate) + "\n"

    # Compute number of auxilary variables are needed:
    self.num_auxilary_variables = self.final_transition_gate - self.num_main_variables

  def __str__(self):
    return '\n Simple Transition Function: ' + \
    '\n  Action vars: ' + str(self.action_vars) + \
    '\n  Parameter vars: ' + str(self.parameter_variable_list) + \
    '\n  Forall vars: ' + str(self.forall_variables_list) + \
    '\n  Static vars: ' + str(self.static_variables) + \
    '\n  First non-static vars: ' + str(self.first_non_static_variables) + \
    '\n  Second non-static vars: ' + str(self.second_non_static_variables) + \
    '\n\n  Variables map: \n' + str(self.string_variables_map) + \
    '\n\n  Transition gates: \n' + str(self.string_transition_gates) + '\n'


  # Takes the new variables and maps them to original transition function
  # and appends to encoding list:
  # WARNING: testing is needed
  def new_transition_copy(self, copy_vars, encoding):
    # Replacing in each gate:
    for gate in self.transition_gates:
      # We ignore comment gates:
      if (len(gate) != 1):
        # Indirectly mapping the list of variables to transition function:
        new_gate_name = copy_vars[gate[1]-1]
        new_gate_list = []
        for prev_gate in gate[2]:
          if prev_gate > 0:
            new_gate_list.append(copy_vars[prev_gate-1])
          else:
            new_gate_list.append(-copy_vars[(-prev_gate)-1])
        encoding.append([gate[0], new_gate_name, new_gate_list])
      else:
        encoding.append([gate[0]])
    
