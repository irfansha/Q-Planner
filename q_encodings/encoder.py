# Irfansha Shaik, 10.04.2021, Aarhus.

from q_encodings.simple_encoding import SimpleEncoding as se
from q_encodings.strongly_constrained_encoding import StronglyConstrainedEncoding as sce
import os

# TODO: add time stamps to the encoding and outputs:

def generate_encoding(tfunc):
  if (tfunc.parsed_instance.args.e == 's-UE'):
    print("Generating simple ungrounded encoding")
    encoding = se(tfunc)
  elif (tfunc.parsed_instance.args.e == 'sc-UE'):
    print("Generating strongly constrained ungrounded encoding")
    encoding = sce(tfunc)

  # We print QCIR format directly to the file:
  if (tfunc.parsed_instance.args.encoding_format == 1):
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.encoding_out)
  else:
    # For QDIMACS, we write the encoding to an intermediate file and change
    # to right format:
    encoding.print_encoding_tofile(tfunc.parsed_instance.args.intermediate_encoding_out)
    converter_tool_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'qcir_to_dimacs_convertor' , 'qcir2qdimacs')
    # Calling the tool
    os.system(converter_tool_path + ' ' + tfunc.parsed_instance.args.intermediate_encoding_out + ' > ' + tfunc.parsed_instance.args.encoding_out)

  # External preprocessing:
  if (tfunc.parsed_instance.args.preprocessing == 1):
    preprocessor_path = os.path.join(tfunc.parsed_instance.args.planner_path, 'tools', 'Bloqqer', 'bloqqer')
    # Calling the tool:
    # We preprocess only qdimacs format encoding:
    assert(tfunc.parsed_instance.args.encoding_format == 2)
    os.system(preprocessor_path + ' ' + tfunc.parsed_instance.args.encoding_out + ' > ' + tfunc.parsed_instance.args.preprocessed_encoding_out)


  # Returning encoding for plan extraction:
  return encoding
