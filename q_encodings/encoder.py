# Irfansha Shaik, 10.04.2021, Aarhus.

from q_encodings.simple_encoding import SimpleEncoding as se
from q_encodings.strongly_constrained_encoding import StronglyConstrainedEncoding as sce
from q_encodings.log_encoding import LogEncoding as le
import os

# TODO: add time stamps to the encoding and outputs:

def add_dependencies_to_qdimacs(parsed_instance, encoding):
  # Read the encoding file:
  f = open(parsed_instance.args.encoding_out, 'r')
  lines = f.readlines()
  f.close()

  header = lines.pop(0)
  previous_line = ''
  for line in lines:
    # Looking at the prefix:
    if (line[0] == 'a' or line[0] == 'e'):
      previous_line = line
    else:
      # this stops the previous line at the last existential layer
      break

  f = open(parsed_instance.args.encoding_out, 'w')

  # Writing the header
  f.write(header)
  # Adding the dependencies:
  for line in encoding.dqdimacs_prefix:
    f.write(line + "\n")
  # Adding the last existential line:
  f.write(previous_line)
  # Adding rest of the clauses:
  for line in lines:
    if (line[0] == 'a' or line[0] == 'e'):
      continue
    else:
      f.write(line)
  f.close()


def generate_encoding(tfunc):
  if (tfunc.parsed_instance.args.e == 's-UE'):
    print("Generating simple ungrounded encoding")
    encoding = se(tfunc)
  elif (tfunc.parsed_instance.args.e == 'sc-UE'):
    print("Generating strongly constrained ungrounded encoding")
    encoding = sce(tfunc)
  elif (tfunc.parsed_instance.args.e == 'l-UE'):
    print("Generating log ungrounded encoding (DQBF)")
    encoding = le(tfunc)

  # We print QCIR format directly to the file:
  if (tfunc.parsed_instance.args.encoding_format == 1):
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.encoding_out)
  elif (tfunc.parsed_instance.args.encoding_format == 2):
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + tfunc.parsed_instance.args.intermediate_encoding_out + ' > ' + tfunc.parsed_instance.args.encoding_out)
  # For now only dqcir is generated:
  elif (tfunc.parsed_instance.args.encoding_format == 3):
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.encoding_out)
  elif (tfunc.parsed_instance.args.encoding_format == 4):
    # For dqdimacs:
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + tfunc.parsed_instance.args.intermediate_encoding_out + ' > ' + tfunc.parsed_instance.args.encoding_out)
    add_dependencies_to_qdimacs(tfunc.parsed_instance, encoding)
  else:
    print("Encoding not available yet!")

  # External preprocessing with bloqqer:
  if (tfunc.parsed_instance.args.preprocessing == 1):
    preprocessor_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'Bloqqer', 'bloqqer')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(tfunc.parsed_instance.args.encoding_format == 2)
    os.system(preprocessor_path + ' ' + tfunc.parsed_instance.args.encoding_out + ' > ' + tfunc.parsed_instance.args.preprocessed_encoding_out)
    print("Preprocessing complete")

  # If we do not enable internal preprocessing:
  if (tfunc.parsed_instance.args.preprocessing == 3 and tfunc.parsed_instance.args.internal_preprocessing == 0):
    preprocessor_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'HQSpre', 'hqspre')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(tfunc.parsed_instance.args.encoding_format == 2 or tfunc.parsed_instance.args.encoding_format == 4)
    os.system(preprocessor_path + ' --timeout ' +  str(tfunc.parsed_instance.args.preprocessing_time_limit) + ' -o ' + tfunc.parsed_instance.args.preprocessed_encoding_out + ' ' + tfunc.parsed_instance.args.encoding_out)
    print("Preprocessing complete")

  if (tfunc.parsed_instance.args.preprocessing == 4):
    preprocessor_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'QRATPre+', 'qratpre+')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(tfunc.parsed_instance.args.encoding_format == 2 or tfunc.parsed_instance.args.encoding_format == 4)
    if (tfunc.parsed_instance.args.run == 1):
      os.system(preprocessor_path + ' --print-formula ' + tfunc.parsed_instance.args.encoding_out + ' ' +  str(tfunc.parsed_instance.args.preprocessing_time_limit)  + ' > ' + tfunc.parsed_instance.args.preprocessed_encoding_out)
    else:
      os.system(preprocessor_path + ' --print-formula --ignore-outermost-vars ' + tfunc.parsed_instance.args.encoding_out + ' ' +  str(tfunc.parsed_instance.args.preprocessing_time_limit)  + ' > ' + tfunc.parsed_instance.args.preprocessed_encoding_out)
    print("Preprocessing complete")


  # Returning encoding for plan extraction:
  return encoding
