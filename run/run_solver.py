# Irfansha Shaik, 11.04.2021, Aarhus.

from run.run_quabs import RunQuabs as rq
from run.plan_extraction import ExtractPlan as ep

def run_single_solver(encoding):
  # For ease of access declaring locally:
  args = encoding.tfunc.parsed_instance.args
  if (args.solver == 1):
    quabs_instance = rq(args)
    sol_map = quabs_instance.sol_map
    if quabs_instance.sat:
      print("Plan found")
    else:
      print("Plan not found")
      return

  # Extracting plan if run >=2:
  if (args.run >= 2):
    ep(encoding, sol_map)
