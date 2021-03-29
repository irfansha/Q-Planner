# Irfansha Shaik, 25.03.2021, Aarhus

from tarski.io import PDDLReader
from predicate_constraints import PredicateConstraints as pc

class Parse:

  # Parses domain and problem file:
  def __init__(self, args):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(args.path + args.domain)
    self.args = args
    self.parsed_problem = reader.parse_instance(self.args.path + self.args.problem)
    # In tarski language is seperated from problem itself:
    self.lang = self.parsed_problem.language
    self.valid_types = []
    self.valid_actions = []

    self.generate_valid_types()
    self.generate_valid_actions()

    # If debug is true we print all the information,
    # here all the parsed information:
    if (args.debug == 2):
      print("#------------------------------------")
      print("PARSED DOMAIN:\n")
      # sorts are types in tarski:
      print("  Types: ", self.lang.sorts)
      print("  Predicates: ", self.lang.predicates)
      # we do not handle functions, (TODO: add assert):
      print("  Functions: ", self.lang.functions)
      # Actions seems to be defined seperately:
      for action_name in self.parsed_problem.actions:
        print("  action: ", action_name)
        action = self.parsed_problem.get_action(action_name)
        #print("    parameters: ", action.parameters, action.parameters[0].sort.name)
        print("    parameter types:")
        for parameter in action.parameters:
          print("      ",parameter, parameter.sort.name)
        # This gives the parameter symbol:
        # print(action.precondition.subformulas[0].subterms[0].symbol)
        print("    preconditions: ", action.precondition)
        print("    effects: ", action.effects)
        #print(action.effects[0].atom.predicate.arity)
      print("#------------------------------------\n")
      print("#------------------------------------")
      print("PARSED PROBLEM:\n")
      print("  Initial State: ", self.parsed_problem.init.as_atoms())
      print("  Goal State: ", self.parsed_problem.goal)
      # constants and objects are combinedly called constants:
      for tp in self.lang.sorts:
        print("  Objects of type " + (tp.name) , list(self.lang.get(tp.name).domain()))


  # Ignoring types with 0 or all objects:
  def generate_valid_types(self):
    num_objects = len(self.lang.constants())
    for typ in self.lang.sorts:
      cur_num_objects = len(list(self.lang.get(typ.name).domain()))
      assert( 0 <= cur_num_objects <= num_objects)
      if (cur_num_objects != 0 and cur_num_objects != num_objects):
        self.valid_types.append(typ)
    # If debug is true we print the valid types:
    if (self.args.debug >= 1):
      print("#-------------------------------------")
      print("VALID TYPES: ", self.valid_types)
      print("#-------------------------------------")


  def generate_valid_actions(self):
    for action_name in self.parsed_problem.actions:
      action = self.parsed_problem.get_action(action_name)
      # Every action is assume valid first,
      # if a parameter with invalid type exists we set flag to 0:
      valid_flag = 1

      for parameter in action.parameters:
        if (parameter.sort not in self.valid_types):
          valid_flag = 0
          break
      # If action is still valid:
      if (valid_flag == 1):
        self.valid_actions.append(action_name)
    # If debug is true we print the valid types:
    if (self.args.debug >= 1):
      print("#-------------------------------------")
      print("VALID ACTIONS: ", self.valid_actions)
      print("#-------------------------------------")



  # Generates predicate specific constraints, in PDDL specification
  # for each action the preconditions and effects are specified here
  # we generate preconditions and effects for each predicate:
  def generate_predicate_constraints(self):

    # First generating constraints for types (static predicates):
    for typ in self.valid_types:
      predicate_constraints = pc(typ.name)
      #print(predicate_constraints)
