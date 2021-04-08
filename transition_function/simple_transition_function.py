# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo
from utils.variables_dispatcher import VarDispatcher as vd

class SimpleTransitionFunction:

  def map_generator(self):
    # TODO: generate log action variables and add to map
    # TODO: generate log varibles for parameters and add to map
    # TODO: generate forall variables
    # TODO: generate static variables and add to map
    # TODO: generate non-static variables of two time steps and add to map
    print(self.variables_map)


  def __init__(self, parsed_instance):
    self.probleminfo = pinfo(parsed_instance)
    self.variables_map = dict()

    #print(probleminfo)
    # Using variable dispatcher for new integer variables:
    transition_variables = vd()

    # TODO: map generator function from variables to integer variables
    self.map_generator()


    # TODO: using the map and new gates generator, add new transition generator

  def __str__(self):
    return 'TODO'