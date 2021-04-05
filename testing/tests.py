# Irfansha Shaik, 05.04.2021, Aarhus.

import testing.blocks_test as bt

def run_tests(args):
  # Testing blocks domain:
  if (bt.test_blocks_domain(args)):
    print("Blocks domain ok...")
  else:
    print("Error in Block domain!")