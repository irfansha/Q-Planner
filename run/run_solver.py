# Irfansha Shaik, 11.04.2021, Aarhus.

from run.run_quabs import RunQuabs as rq

def run_single_solver(args):
  if (args.solver == 1):
    quabs_instance = rq(args)
    if quabs_instance.sat:
      print("Plan found")
    else:
      print("Plan not found")
