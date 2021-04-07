# Irfansha Shaik, 07.04.2021, Aarhus.

class ProblemInfo:

  def __init__(self, parsed_instance):
    self.static_predicates = []
    self.non_static_predicates = []
    self.valid_actions = parsed_instance.valid_actions
    self.objects = parsed_instance.lang.constants()

    # Looping through predicates to sort static and non-static predicates:
    for single_predicate_constraints in parsed_instance.predicate_constraints:
      print(single_predicate_constraints)




    self.num_static_predicates = 0
    self.num_non_static_predicates = 0
    self.num_valid_actions = 0
    self.num_objects = len(self.objects)

  def __str__(self):
    return '\n Problem parsed info: ' + \
    '\n  static predicates: ' + str(self.static_predicates) + \
    '\n  non-static predicates: ' + str(self.non_static_predicates) + \
    '\n  valid actions: ' + str(self.valid_actions) + \
    '\n  objects: ' + str(self.objects) + '\n'