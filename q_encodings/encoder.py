# Irfansha Shaik, 10.04.2021, Aarhus.

from q_encodings.simple_encoding import SimpleEncoding as se
import os

# TODO: add time stamps to the encoding and outputs:

def generate_encoding(tfunc):
  if (tfunc.parsed_instance.args.e == 's-UE'):
    print("Generating simple ungrounded encoding")
    encoding = se(tfunc)

  # We print QCIR format directly to the file:
  if (tfunc.parsed_instance.args.encoding_format == 1):
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.encoding_out)
  else:
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    # TODO: Better to make the intermediate file path remote:
    intermediate_file_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'intermediate_files', 'intermediate_qcir_encoding')
    encoding.print_encoding_tofile(intermediate_file_path)
    converter_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + intermediate_file_path + ' > ' + tfunc.parsed_instance.args.encoding_out)

  # Returning encoding for plan extraction:
  return encoding
