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
    self.generate_type_bounds()


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

  # First sorts the objects list based on types i.e., groups them based on object type and type with less objects goes front,
  # then finds the bounds for each type (including compound types):
  def generate_type_bounds(self):
    base_types = []
    for obj in self.lang.constants():
      if (obj.sort.name not in base_types):
        #print(list(self.lang.get(obj.sort.name).domain()))
        base_types.append(obj.sort.name)
    #print(base_types)
    #print(self.lang.constants())
    # Sorting by number of objects present in the type:
    base_types.sort(key = lambda x:len(list(self.lang.get(x).domain())))
    #print(base_types)

    self.new_objects_list = []
    self.type_bounds = {}
    # we use index for indicating bounds for each base type:
    start_index = 0
    # Generating new objects list that is sorted based on base types:
    for single_base_type in base_types:
      cur_type_objects = list(self.lang.get(single_base_type).domain())
      self.new_objects_list.extend(cur_type_objects)
      # Base types only have single bound but adding inside list for generality:
      self.type_bounds[single_base_type] = [[start_index, len(cur_type_objects)-1 + start_index]]
      start_index = len(cur_type_objects) + start_index
      # The new index must be the same as the length of the current new object list:
      assert(start_index == len(self.new_objects_list))

    #print(len(self.new_objects_list))
    #print(self.type_bounds)
    # Finding base types for each compound type:
    for type in self.valid_types:
      if (type.name not in base_types):
        # First adding empty list for current type:
        self.type_bounds[type.name] = []
        cur_type_objects = list(self.lang.get(type.name).domain())
        #print(type.name, cur_type_objects)
        # If type is super types i.e., all the objects are this type then we ignore:
        if len(list(cur_type_objects)) == len(self.new_objects_list):
          continue
        # Now we loop through the objects of this types to find the sub-base type bounds:
        for obj in cur_type_objects:
          # Base types only have on type:
          sub_type_bound = self.type_bounds[obj.sort.name][0]
          if (sub_type_bound not in self.type_bounds[type.name]):
            self.type_bounds[type.name].append(sub_type_bound)
          #print(obj.name, obj.sort.name, sub_type_bound)

    #print(self.type_bounds)

    # Sorting the bounds in type bounds, this way it is possible to combine adjacent intervals:
    for cur_type,cur_bounds in self.type_bounds.items():
      cur_bounds.sort(key = lambda x:int(x[0]))

    for cur_type, cur_bounds in self.type_bounds.items():
      # We only look at the compound types:
      if (len(cur_bounds) < 2):
        continue
      new_consolidated_bounds = []

      prev_bound = cur_bounds[0]
      for bound in cur_bounds[1:]:
        if prev_bound[1] + 1 == bound[0]:
          prev_bound = [prev_bound[0], bound[1]]
        else:
          # If the current bound is not a continution then we add it to the consodidated bounds:
          new_consolidated_bounds.append(prev_bound)
          # The current bound will then become the previous bound for the next round:
          prev_bound = bound
      # Last bound must be added to the consolidated bounds:
      new_consolidated_bounds.append(prev_bound)
      self.type_bounds[cur_type] = list(new_consolidated_bounds)

    #print(self.type_bounds)


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