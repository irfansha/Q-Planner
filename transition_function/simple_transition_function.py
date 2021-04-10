# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo
from utils.variables_dispatcher import VarDispatcher as vd
from utils.gates import GatesGen as gg

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
      # Representation in binary requires number of action variables:
      rep_string = '0' + str(self.probleminfo.num_action_variables) + 'b'
      bin_string = format(i, rep_string)
      cur_action_variable_list = []
      # Depending on the binary string we set action variables to '+' or '-':
      for j in range(self.probleminfo.num_action_variables):
        if (bin_string[j] == '0'):
          cur_action_variable_list.append(-self.action_vars[j])
        else:
          cur_action_variable_list.append(self.action_vars[j])
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
      # TODO: handle if a parameter is constant:
      assert('?' in parameter)
      parameter_variables = self.variables_map[(action_name, parameter)]
      forall_varaibles = self.forall_variables_list[i]
      # Printing for redability:
      self.transition_gates.append(['# Equality gate for action parameter: (' + str(action_name) + ',' + str(parameter) + ') and ' + str(i) + 'th forall variables'])
      self.transition_gates.append(['# parameter vars : (' + ', '.join(str(x) for x in parameter_variables) + ')'])
      self.transition_gates.append(['# forall vars : (' + ', '.join(str(x) for x in forall_varaibles) + ')'])

      self.gates_generator.complete_equality_gate(parameter_variables, forall_varaibles)
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
    # Generate if then gate for the predicate:
    self.transition_gates.append(['# If then gate for the predicate:'])
    self.gates_generator.if_then_gate(self.gates_generator.output_gate, predicate_variable)


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
            self.constraints_generator(single_predicate_constraints.pos_eff, self.variables_map[non_static_predicate, 'second'])
            predicate_final_gates.append(self.gates_generator.output_gate)
            effect_gates.append(self.gates_generator.output_gate)
          # Negative effect constraints:
          self.transition_gates.append(['# Negative effects: '])
          if (len(single_predicate_constraints.neg_eff) != 0):
            self.constraints_generator(single_predicate_constraints.neg_eff, -self.variables_map[non_static_predicate, 'second'])
            predicate_final_gates.append(self.gates_generator.output_gate)
            effect_gates.append(self.gates_generator.output_gate)

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


      # Add seperator in encoding for better redability:
      self.transition_gates.append(["# ------------------------------------------------------------------------"])

    # TODO: add constraints for not possible actions and parameter combinations

    # TODO: equality gates, only with parameter variables:
    for single_predicate_constraints in self.parsed_instance.predicate_constraints:
      if (single_predicate_constraints.name == '='):
        assert(len(single_predicate_constraints.pos_pre) == 0 and len(single_predicate_constraints.neg_pre) == 0)

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
    for gate in self.transition_gates:
        self.string_transition_gates += str(gate) + "\n"

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
    
