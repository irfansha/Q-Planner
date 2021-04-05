# Irfansha Shaik, 05.04.2021, Aarhus.

import os
import zipfile
import testing.blocks_test as bt

def run_tests(args):
  # Check if the zipped testcases are unzipped,
  # if not, unzipping them:
  if(not os.path.exists(os.path.join(os.getcwd(), 'testing' , 'testcases'))):
    print("Unzipping testcases")
    testcases_zip_path = os.path.join(os.getcwd(), 'testing' , 'testcases.zip')
    current_directory = os.path.join(os.getcwd(), 'testing')
    with zipfile.ZipFile(testcases_zip_path, 'r') as zip_ref:
      zip_ref.extractall(current_directory)

  # Testing blocks domain:
  if (bt.test_blocks_domain(args)):
    print("Blocks domain ok...")
  else:
    print("Error in Block domain!")