# Irfansha Shaik, 10.04.2021, Aarhus.

from q_encodings.simple_encoding import SimpleEncoding as se

def generate_encoding(tfunc):
  if (tfunc.parsed_instance.args.e == 's-UE'):
    print("Generating simple ungrounded encoding")
    encoding = se(tfunc)

  # TODO: write the encoding to the right file
  encoding.print_encoding_tofile(tfunc.parsed_instance.args.encoding_out)

  # TODO: change the encoding to qdimacs using tools
