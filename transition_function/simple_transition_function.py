# Irfansha Shaik, 07.04.2021, Aarhus

from constraints.problem_structure import ProblemInfo as pinfo

class SimpleTransitionFunction:

  def __init__(self, parsed_instance):
    probleminfo = pinfo(parsed_instance)
    print(probleminfo)

  def __str__(self):
    return 'TODO'