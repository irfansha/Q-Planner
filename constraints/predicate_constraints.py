# Irfansha Shaik, 29.03.2021, Aarhus

class PredicateConstraints:

  def __init__(self, name):
    self.name = name
    self.pos_pre = []
    self.neg_pre = []
    self.pos_eff = []
    self.neg_eff = []

  def __str__(self):
    return '  prediate: ' + self.name + \
    '\n    positive preconditions: ' + str(self.pos_pre) + \
    '\n    negative_preconditions: ' + str(self.neg_pre) + \
    '\n    positive_effects: ' + str(self.pos_eff) + \
    '\n    negative_effects: ' + str(self.neg_eff) + '\n'

  # Action name and predicate parameters are added as a tuple,
  # predicate parameters are a list here:
  def add_pospre_constraint(self, action_name, predicate_parameters):
    assert(type(predicate_parameters) == list)
    self.pos_pre.append((action_name, predicate_parameters))
  def add_negpre_constraint(self, action_name, predicate_parameters):
    assert(type(predicate_parameters) == list)
    self.neg_pre.append((action_name, predicate_parameters))
  def add_poseff_constraint(self, action_name, predicate_parameters):
    assert(type(predicate_parameters) == list)
    self.pos_eff.append((action_name, predicate_parameters))
  def add_negeff_constraint(self, action_name, predicate_parameters):
    assert(type(predicate_parameters) == list)
    self.neg_eff.append((action_name, predicate_parameters))
