# Irfansha Shaik, 25.03.2021, Aarhus

import os
from tarski.io import PDDLReader
from tarski.syntax import formulas as fr
from tarski.fstrips import fstrips as fs
from constraints.predicate_constraints import PredicateConstraints as pc

class Parse:

  # Parses domain and problem file:
  def __init__(self, args):
    reader = PDDLReader(raise_on_error=True)
    domain_path = os.path.join(args.path, args.domain)
    problem_path = os.path.join(args.path, args.problem)
    reader.parse_domain(domain_path)
    self.args = args
    self.parsed_problem = reader.parse_instance(problem_path)
    # In tarski language is seperated from problem itself:
    self.lang = self.parsed_problem.language
    self.already_solved = 0

    # Asserting the goal is not already satisfied:
    if(self.parsed_problem.init[self.parsed_problem.goal]):
      self.already_solved = 1
      print("problem is trivially true")

    self.valid_types = []
    # better to have something to look up directly for:
    self.valid_type_names = []
    self.valid_actions = []

    # WARNING: Possible problem here,
    # since we are trimming down some types and actions
    # debugging to be done here in case something goes wrong:
    self.generate_valid_types()
    self.generate_valid_actions()

    # Asserting no functions present:
    assert(len(self.lang.functions) == 0)

    # If debug is true we print all the information,
    # here all the parsed information:
    if (args.debug == 2):
      print("#------------------------------------------------------------------------")
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
      print("#------------------------------------------------------------------------\n")
      print("PARSED PROBLEM:\n")
      print("  Initial State: ", self.parsed_problem.init.as_atoms())
      print("  Goal State: ", self.parsed_problem.goal)
      print("  Objects: ", self.lang.constants())
      print(self.lang.sorts)
      # constants and objects are combinedly called constants:
      for tp in self.lang.sorts:
        print("  Objects of type " + (tp.name) , list(self.lang.get(tp.name).domain()))
      print("#------------------------------------------------------------------------\n")


  # Ignoring types with 0 objects:
  def generate_valid_types(self):
    for typ in self.lang.sorts:
      cur_num_objects = len(list(self.lang.get(typ.name).domain()))
      if (cur_num_objects != 0):
        self.valid_types.append(typ)
        self.valid_type_names.append(typ.name)
    # If debug is true we print the valid types:
    if (self.args.debug >= 1):
      print("#------------------------------------------------------------------------")
      print("VALID TYPES: ", self.valid_types)
      print("VALID TYPE NAMES: ", self.valid_type_names)
      print("#------------------------------------------------------------------------\n")


  def generate_valid_actions(self):
    for action_name in self.parsed_problem.actions:
      action = self.parsed_problem.get_action(action_name)
      # Every action is assume valid first,
      # if a parameter with invalid type exists we set flag to 0:
      valid_flag = 1

      for parameter in action.parameters:
        if (parameter.sort not in self.valid_types):
          valid_flag = 0
          if (self.args.debug >= 1):
            print(action_name)
          break
      # If action is still valid:
      if (valid_flag == 1):
        self.valid_actions.append(action_name)
    # If debug is true we print the valid types:
    if (self.args.debug >= 1):
      print("#------------------------------------------------------------------------")
      print("VALID ACTIONS: ", self.valid_actions)
      print("Num of valid actions: ", len(self.valid_actions))
      print("#------------------------------------------------------------------------\n")


  # Helper function to get the parameter symbols of
  # a single predicate:
  def get_parameter_symbols(self, subformula):
    parameter_list = []
    for subterm in subformula.subterms:
      parameter_list.append(subterm.symbol)
    return parameter_list


  # Generates predicate specific constraints, in PDDL specification
  # for each action the preconditions and effects are specified here
  # we generate preconditions and effects for each predicate:
  def generate_predicate_constraints(self):

    self.predicate_constraints = []

    # First generating constraints for types (static predicates):
    for typ in self.valid_types:
      # If all objects are same type we ignore the type,
      # WARNING: errors possible debugging to be done if something is wrong:
      num_objects = len(self.lang.constants())
      cur_num_objects = len(list(self.lang.get(typ.name).domain()))
      if (cur_num_objects == num_objects):
        continue
      single_predicate_constraints = pc(typ.name)
      for action_name in self.valid_actions:
        action = self.parsed_problem.get_action(action_name)
        for parameter in action.parameters:
          if (parameter.sort.name == typ.name):
            single_predicate_constraints.add_pospre_constraint(action_name, [parameter.symbol])
      self.predicate_constraints.append(single_predicate_constraints)

    # For each normal predicates, we add constraints from each action,
    # WARNING: generating constraints, errors possible,
    # TODO: add rigorous testing for several domains:
    for predicate in self.lang.predicates:
      # Handling =, != symbols by converting them to strings:
      single_predicate_constraints = pc(str(predicate.name))
      for action_name in self.valid_actions:
        action = self.parsed_problem.get_action(action_name)
        # If single condition, then not a compound formula
        # so handling both conditions:
        if (fr.is_atom(action.precondition)):
          preconditions_list = [action.precondition]
        elif(isinstance(action.precondition, fr.Tautology)):
          preconditions_list = []
        else:
          assert(action.precondition.connective == fr.Connective.And)
          preconditions_list = action.precondition.subformulas
        # Adding preconditons to constraints:
        for precondition in preconditions_list:
          # If it is negative atom, then we need to consider as
          # compund formula:
          if(fr.is_neg(precondition)):
            # Asserting negation connective:
            assert(precondition.connective == fr.Connective.Not)
            # Asserting single precondition:
            assert(len(precondition.subformulas) == 1)
            cur_predicate = precondition.subformulas[0]
            if(cur_predicate.predicate.name == predicate.name):
              single_predicate_constraints.add_negpre_constraint(action_name, self.get_parameter_symbols(cur_predicate))
          else:
            if (precondition.predicate.name == predicate.name):
              single_predicate_constraints.add_pospre_constraint(action_name, self.get_parameter_symbols(precondition))
        # Adding effects to constraints:
        for effect in action.effects:
          if (isinstance(effect, fs.AddEffect)):
            if (effect.atom.predicate.name == predicate.name):
              single_predicate_constraints.add_poseff_constraint(action_name, self.get_parameter_symbols(effect.atom))
          elif(isinstance(effect, fs.DelEffect)):
            if (effect.atom.predicate.name == predicate.name):
              single_predicate_constraints.add_negeff_constraint(action_name, self.get_parameter_symbols(effect.atom))
          else:
            # Must not be reachable yet:
            assert(True)
            print("TODO: handle conditional effects")
            #print(effect, effect.atom.predicate)
      self.predicate_constraints.append(single_predicate_constraints)


    if (self.args.debug >= 1):
      print("#------------------------------------------------------------------------\n")
      print("Predicate constraints: ")
      for single_predicate_constraints in self.predicate_constraints:
        print(single_predicate_constraints)
      print("#------------------------------------------------------------------------\n")

  # Generates predicate specific constraints, in PDDL specification
  # for each action the preconditions and effects are specified here
  # we generate preconditions and effects for each predicate:
  def generate_only_nonstatic_predicate_constraints(self):

    self.predicate_constraints = []

    # TODO: also remove static predicates
    # For each normal predicates, we add constraints from each action,
    # WARNING: generating constraints, errors possible,
    # TODO: add rigorous testing for several domains:
    for predicate in self.lang.predicates:
      # Handling =, != symbols by converting them to strings:
      single_predicate_constraints = pc(str(predicate.name))
      for action_name in self.valid_actions:
        action = self.parsed_problem.get_action(action_name)
        # If single condition, then not a compound formula
        # so handling both conditions:
        if (fr.is_atom(action.precondition)):
          preconditions_list = [action.precondition]
        elif(isinstance(action.precondition, fr.Tautology)):
          preconditions_list = []
        else:
          assert(action.precondition.connective == fr.Connective.And)
          preconditions_list = action.precondition.subformulas
        # Adding preconditons to constraints:
        for precondition in preconditions_list:
          # If it is negative atom, then we need to consider as
          # compund formula:
          if(fr.is_neg(precondition)):
            # Asserting negation connective:
            assert(precondition.connective == fr.Connective.Not)
            # Asserting single precondition:
            assert(len(precondition.subformulas) == 1)
            cur_predicate = precondition.subformulas[0]
            if(cur_predicate.predicate.name == predicate.name):
              single_predicate_constraints.add_negpre_constraint(action_name, self.get_parameter_symbols(cur_predicate))
          else:
            if (precondition.predicate.name == predicate.name):
              single_predicate_constraints.add_pospre_constraint(action_name, self.get_parameter_symbols(precondition))
        # Adding effects to constraints:
        for effect in action.effects:
          if (isinstance(effect, fs.AddEffect)):
            if (effect.atom.predicate.name == predicate.name):
              single_predicate_constraints.add_poseff_constraint(action_name, self.get_parameter_symbols(effect.atom))
          elif(isinstance(effect, fs.DelEffect)):
            if (effect.atom.predicate.name == predicate.name):
              single_predicate_constraints.add_negeff_constraint(action_name, self.get_parameter_symbols(effect.atom))
          else:
            # Must not be reachable yet:
            assert(True)
            print("TODO: handle conditional effects")
            #print(effect, effect.atom.predicate)
      self.predicate_constraints.append(single_predicate_constraints)


    if (self.args.debug >= 1):
      print("#------------------------------------------------------------------------\n")
      print("Predicate constraints: ")
      for single_predicate_constraints in self.predicate_constraints:
        print(single_predicate_constraints)
      print("#------------------------------------------------------------------------\n")