# The time required to use Ocean to build the up, down, front and back
# subQUBOs is rather lengthy - perhaps one to two hours.  These four
# subQUBOs are identical in form, and so rather than generate all four
# independently, we can generate one of the four subQUBOs and then
# rename the variables in that QUBO to create any of the other QUBOs.
#
# This utility requires two arguments: the first is the input QUBO
# which contains a SymPy polynomial written as a pickle file.  The
# second argument is the output QUBO which is generated from the
# input by changing variable names.  The replacement applied
# to the variable names changes the first letter of the input name
# (i.e., 'u', 'd', 'f', 'b'} to the first letter of the output name.
#
# Since the DEQO algorithm is relatively fast this utility only
# applies to Ocean generated subQUBOs.

import pickle
import sys
import sympy
import sympy_util

usage_message = 'usage: rename_subqubo.py {up|down|front|back} {up|down|front|back}'

if len(sys.argv) != 3:
    print(usage_message)
    sys.exit(1)
    
input = sys.argv[1]
output = sys.argv[2]

input_file = input + '.ocean.pickle'
output_file = output + '.ocean.pickle'

try:
    with open(input_file, 'rb') as in_f:
        expr = pickle.load(in_f)

    rename_sym_dict = dict()
    all_vars = sympy_util.poly_vars(expr)
    for var in all_vars:
        trans_var = var.name.replace(input[0] + '_', output[0] + '_')
        rename_sym_dict[var] = sympy.symbols(trans_var)

    trans_expr = expr.subs(rename_sym_dict)

except FileNotFoundError:
    print('Error: input file "%s" does not exist' % input_file)
    sys.exit(1)

with open(output_file, 'wb') as out_f:
    pickle.dump(trans_expr, out_f, pickle.HIGHEST_PROTOCOL)
