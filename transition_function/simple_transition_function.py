# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo
from utils.variables_dispatcher import VarDispatcher as vd

class SimpleTransitionFunction:

  def map_generator(self, parsed_instance):
    # TODO: Add all variables to map

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
      action = parsed_instance.parsed_problem.get_action(action_name)
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


  def __init__(self, parsed_instance):
    self.probleminfo = pinfo(parsed_instance)
    self.variables_map = dict()
    self.string_variables_map = ''

    if (parsed_instance.args.debug >= 1):
      print(self.probleminfo)
    # Using variable dispatcher for new integer variables:
    self.transition_variables = vd()

    # Mapping variables to integer variables for encoding:
    self.map_generator(parsed_instance)
    self.string_variables_map = "   {" + "\n    ".join("{!r}: {!r},".format(k, v) for k, v in self.variables_map.items()) + "}"

    # TODO: using the map and new gates generator, add new transition generator


  def __str__(self):
    return '\n Simple Transition Function: ' + \
    '\n  Action vars: ' + str(self.action_vars) + \
    '\n  Parameter vars: ' + str(self.parameter_variable_list) + \
    '\n  Forall vars: ' + str(self.forall_variables_list) + \
    '\n  Static vars: ' + str(self.static_variables) + \
    '\n  First non-static vars: ' + str(self.first_non_static_variables) + \
    '\n  Second non-static vars: ' + str(self.second_non_static_variables) + \
    '\n\n  Variables map: \n' + str(self.string_variables_map) + '\n'