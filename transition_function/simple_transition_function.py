# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo
from utils.variables_dispatcher import VarDispatcher as vd

class SimpleTransitionFunction:

  def __init__(self, parsed_instance):
    probleminfo = pinfo(parsed_instance)
    print(probleminfo)
    # Using variable dispatcher for new integer variables:
    transition_variables = vd()

    # TODO: map generator function from variables to integer variables

    # TODO: using the map and new gates generator, add new transition generator

  def __str__(self):
    return 'TODO'