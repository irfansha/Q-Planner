# Irfansha Shaik, 30.04.2021, Aarhus

import os

class RunCpddl:

  def run(self):
    # Calling the tool
    os.system(self.cpddl_tool_path + ' -q ' + self.domain_path + ' ' + self.problem_path + ' > ' + self.invariants_out)

  def __init__(self, tfunc):
    self.domain_path = os.path.join(tfunc.parsed_instance.args.path, tfunc.parsed_instance.args.domain)
    self.problem_path = os.path.join(tfunc.parsed_instance.args.path, tfunc.parsed_instance.args.problem)
    self.cpddl_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'cpddl' , 'pddl-lifted-mgroups')
    self.invariants_out = tfunc.parsed_instance.args.invariants_out
    self.run()
    # TODO: Parse and update the invariants generated