# Irfansha Shaik, 07.04.2021, Aarhus.

class ProblemInfo:

  def __init__(self, parsed_instance):
    self.static_predicates = []
    self.non_static_predicates = []
    self.valid_actions = parsed_instance.valid_actions
    self.objects = parsed_instance.lang.constants()

    # Looping through predicates to sort static and non-static predicates:
    for single_predicate_constraints in parsed_instance.predicate_constraints:
      # We handle equality and inequality separately:
      if (single_predicate_constraints.name == '=' or single_predicate_constraints.name == '!='):
        continue
      if (len(single_predicate_constraints.pos_eff) == 0 and len(single_predicate_constraints.neg_eff) == 0):
        # We do not need non-used predicates:
        if (len(single_predicate_constraints.pos_pre) != 0 or len(single_predicate_constraints.neg_pre) != 0):
          self.static_predicates.append(single_predicate_constraints.name)
      else:
        self.non_static_predicates.append(single_predicate_constraints.name)

    self.num_static_predicates = len(self.static_predicates)
    self.num_non_static_predicates = len(self.non_static_predicates)
    self.num_valid_actions = len(self.valid_actions)
    self.num_objects = len(self.objects)
    # To be updated to correct values:
    self.max_action_parameters = 0
    self.max_predicate_parameters = 0
    # if valid types are present we start the max static predicates with 1,
    # WARNING: some error might creep in here:
    if (len(parsed_instance.valid_types) == 0):
      self.max_static_predicate_parameters = 0
    else:
      self.max_static_predicate_parameters = 1
    self.max_non_static_predicate_parameters = 0

    for predicate in parsed_instance.lang.predicates:
      if (predicate.name in self.static_predicates):
        if (self.max_static_predicate_parameters < predicate.arity):
          self.max_static_predicate_parameters = predicate.arity
      elif (predicate.name in self.non_static_predicates):
        if (self.max_non_static_predicate_parameters < predicate.arity):
          self.max_non_static_predicate_parameters = predicate.arity

    # maximum of static and non static predicates results in the overall maximum:
    if (self.max_static_predicate_parameters > self.max_non_static_predicate_parameters):
      self.max_predicate_parameters = self.max_static_predicate_parameters
    else:
      self.max_predicate_parameters = self.max_non_static_predicate_parameters

    # Getting max parameters of valid actions:
    for action_name in self.valid_actions:
      action = parsed_instance.parsed_problem.get_action(action_name)
      if (self.max_action_parameters < len(action.parameters)):
        self.max_action_parameters = len(action.parameters)

  def __str__(self):
    return '\n Problem parsed info: ' + \
    '\n  static predicates: ' + str(self.static_predicates) + \
    '\n  non-static predicates: ' + str(self.non_static_predicates) + \
    '\n  valid actions: ' + str(self.valid_actions) + \
    '\n  objects: ' + str(self.objects) + \
    '\n\n  number of static predicates: ' + str(self.num_static_predicates) + \
    '\n  number of non-static predicates: ' + str(self.num_non_static_predicates) + \
    '\n\n  max static predicates arity: ' + str(self.max_static_predicate_parameters) + \
    '\n  max non-static predicates arity: ' + str(self.max_non_static_predicate_parameters) + \
    '\n  max predicates arity: ' + str(self.max_predicate_parameters) + \
    '\n\n  max actions arity: ' + str(self.max_action_parameters) + \
    '\n\n  number of valid actions: ' + str(self.num_valid_actions) + \
    '\n  number of objects: ' + str(self.num_objects) + '\n'