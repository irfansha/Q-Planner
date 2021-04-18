# Irfansha Shaik, 16.04.2021, Aarhus.

import os


competition_sat_list = [("IPC1", "gripper", "prob01.pddl", 11), ("IPC1", "movie", "prob01.pddl", 7),
                        ("IPC1","movie", "prob02.pddl", 7),
                        ("IPC2","Blocks", "prob01.pddl", 6), ("IPC2","Blocks", "prob02.pddl",12),
                        ("IPC2","Elevator", "prob01.pddl", 4), ("IPC2","Elevator", "prob02.pddl", 10),
                        ("IPC3","DriverLog", "prob01.pddl", 7),
                        ("IPC4","Satellite", "prob01.pddl", 9), ("IPC4","Satellite", "prob02.pddl", 13),
                        ("IPC5","Rovers", "prob01.pddl", 10), ("IPC5","Rovers", "prob02.pddl", 8)]

competition_unsat_list = [("IPC1","gripper", "prob01.pddl", 10), ("IPC1","movie", "prob01.pddl", 6),
                          ("IPC1","movie", "prob02.pddl", 6),
                          ("IPC2","Blocks", "prob01.pddl", 5), ("IPC2","Blocks", "prob02.pddl",11),
                          ("IPC2","Elevator", "prob01.pddl", 3), ("IPC2","Elevator", "prob02.pddl", 9),
                          ("IPC3","DriverLog", "prob01.pddl", 6),
                          ("IPC4","Satellite", "prob01.pddl", 8), ("IPC4","Satellite", "prob02.pddl", 12),
                          ("IPC5","Rovers", "prob01.pddl", 9), ("IPC5","Rovers", "prob02.pddl", 7)]



def gen_new_arguments(path, domain, problem, k, args):
  new_command = ''
  for arg in vars(args):
    # We set these separately:
    if (arg == 'version'):
      continue
    elif (arg == 'path'):
      new_command += ' --path ' + path
    elif (arg == '--domain'):
      new_command += ' --domain ' + domain
    elif(arg == 'problem'):
      new_command += ' --problem ' + problem
    elif(arg == 'plan_length'):
      new_command += ' --plan_length ' + str(k)
    elif(arg == "testing"):
      new_command += ' --testing 0'
    elif(arg == "val_testing"):
      new_command += ' --val_testing 0'
    elif(arg == "debug"):
      new_command += ' --debug 0'
    elif( arg == "run_tests"):
      new_command += ' --run_tests 0'
    elif (len(arg) == 1):
      new_command += ' -' + str(arg) + ' ' + str(getattr(args, arg))
    else:
      new_command += ' --' + str(arg) + ' ' + str(getattr(args, arg))
  return(new_command)


def run_tests(args):
    count = 0
    all_success = 1
    competition_testcase_path = os.path.join(args.planner_path, 'testing', 'testcases', 'competition')
    # Running testcases that have a plan:
    for testcase in competition_sat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      path = os.path.join(args.planner_path,competition_testcase_path, testcase[0], testcase[1])
      domain = 'domain.pddl'
      problem = testcase[2]
      print(path, domain, problem, testcase[3])
      # domain and problem files (and k) are new:
      command_arguments = gen_new_arguments(path, domain, problem, testcase[3], args)
      # Running testcase and generating plan (if available):
      command = 'python3 qplanner.py ' + command_arguments
      plan_status = os.popen(command).read()
      print(plan_status)
      if (args.run == 1):
        print("Testing only existence")
        if ('Plan found' in plan_status):
          print("success")
        else:
          # plan failed:
          all_success = 0
          print("failed! plan must exist")
      elif ('Plan found' in plan_status):
        # Validating the plan generated:
        Val_path = os.path.join(args.planner_path,"tools", "VAL" ,"Validate")
        domain_full_path = os.path.join(path, 'domain.pddl')
        problem_full_path = os.path.join(path, testcase[2])
        command = Val_path + ' ' + domain_full_path + ' ' + problem_full_path + ' ' + args.plan_out
        testing_status = os.popen(command).read()
        if ("Plan valid" not in testing_status):
          print("failed")
          # plan failed:
          all_success = 0
          exit()
        else:
          print("success")
      else:
          print("failed! plan must exist")
          # plan failed:
          all_success = 0
      print("--------------------------------------------------------------------------------\n")
    # Running unsat testcases:
    for testcase in competition_unsat_list:
      count += 1
      print("\n--------------------------------------------------------------------------------")
      print("testcase" + str(count) + " :")
      path = os.path.join(args.planner_path,competition_testcase_path, testcase[0], testcase[1])
      domain = 'domain.pddl'
      problem = testcase[2]
      print(path, domain, problem, testcase[3])
      # domain and problem files (and k) are new:
      command_arguments = gen_new_arguments(path,domain, problem, testcase[3], args)
      # Running testcase and generating plan (if available):
      command = 'python3 qplanner.py ' + command_arguments
      plan_status = os.popen(command).read()
      print(plan_status)
      if ('Plan not found' in plan_status):
        print("success")
      else:
        # plan failed:
        all_success = 0
        print("failed! plan must not exist")
      print("--------------------------------------------------------------------------------\n")

    if (all_success):
      print("All tests successful")
    else:
      print("Test failed")