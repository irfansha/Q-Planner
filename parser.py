# Irfansha Shaik, 25.03.2021, Aarhus

from tarski.io import PDDLReader

# Parses domain and problem file,
# TODO: remove unnecessary tokens
#   Steps:
#   1. trim down types which are not defined in objects
def parse(args):
  reader = PDDLReader(raise_on_error=True)
  reader.parse_domain(args.path + args.domain)
  parsed_problem = reader.parse_instance(args.path + args.problem)
  # In tarski language is seperated from problem itself:
  lang = parsed_problem.language

  # If debug is true we print all the information,
  # here all the parsed information:
  if (args.debug == 1):
    print("#------------------------------------")
    print("Parsed Domain:")
    # sorts are types in tarski:
    print("Types: ", lang.sorts)
    print("Predicates: ", lang.predicates)
    # we do not handle functions, (TODO: add assert):
    print("Functions: ", lang.functions)
    # Actions seems to be defined seperately:
    for action_name in parsed_problem.actions:
      print("action: ", action_name)
      action = parsed_problem.get_action(action_name)
      print("  parameters: ", action.parameters[0], action.parameters[0].sort.name)
      print("  parameter types:")
      # TODO: need to able to specify parameter for each predicate inside conditions:
      for parameter in action.parameters:
        print("    ",parameter, parameter.sort.name)
      print("  preconditions: ", action.precondition)
      print("  effects: ", action.effects)
    print("#------------------------------------\n")
    print("#------------------------------------")
    print("Parsed problem instance:")
    print("Initial State: ", parsed_problem.init.as_atoms())
    print("Goal State: ", parsed_problem.goal)
    # constants and objects are combinedly called constants:
    for tp in lang.sorts:
      print("Objects of type " + (tp.name) , list(lang.get(tp.name).domain()))