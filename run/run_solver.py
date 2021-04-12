# Irfansha Shaik, 11.04.2021, Aarhus.

from run.run_quabs import RunQuabs as rq
from run.run_caqe import RunCaqe as rc
from run.plan_extraction import ExtractPlan as ep
import testing.val_testing as vt

def run_single_solver(encoding):
  # For ease of access declaring locally:
  args = encoding.tfunc.parsed_instance.args
  if (args.solver == 1):
    instance = rq(args)
    sol_map = instance.sol_map
  elif (args.solver == 2):
    instance = rc(args)
    sol_map = instance.sol_map

  # Checking existence of plan:
  if instance.sat == 1:
    print("Plan found")
  else:
    print("Plan not found")
    return

  # Extracting plan if run >=2:
  if (args.run >= 2):
    ep(encoding, sol_map)

  if (args.val_testing == 1):
    vt.test_plan_with_val(args)
