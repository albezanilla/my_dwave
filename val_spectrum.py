# This utility checks the spectrum of a QUBO by evaluating it for each
# valid setting of the logical variables and displaying the histogram
# of objective values up to a hard-wired limit.  It also computes a
# histogram of all states for which the logical variables are not
# equal to a valid state and displays that histogram.

import pickle
import ii
import validate
from sympy import symbols
import sys

usage_message = 'Usage: val_spectrum.py {deqo|ocean} {cube1|cube2|cube3|cube4|up|down|front|back}'

methods = {'deqo', 'ocean'}
subqubos = {'cube1', 'cube2', 'cube3', 'cube4', 'up', 'down', 'front', 'back'}

# These are the hard-wired limits on the range of objective values
# displayed for valid and invalid states:
valid_obj_limit = 10
invalid_obj_limit = 20

if len(sys.argv) == 3 and sys.argv[1] in methods and sys.argv[2] in subqubos:
    method = sys.argv[1]
    subqubo = sys.argv[2]

    filename = subqubo + '.' + method + '.pickle'
    
    try:
        with open(filename, 'rb') as f:
            qubo = pickle.load(f)
    except FileNotFoundError:
        print('error: file "%s" does not exist' % filename)
        sys.exit(1)

    if subqubo[0:4] == 'cube':
        cube_num = int(subqubo[4])
        logical_vars, valid_states = ii.cube_configurations(cube_num)
    else:
        logical_vars, valid_states = ii.face_configurations(subqubo[0])

    logical_syms = tuple(symbols(logical_vars))
    valid_states_hist, invalid_states_hist = validate.spectrum(logical_syms, valid_states, qubo)

    print('***** Variable ordering *****')
    for var in logical_vars:
        print(var)

    print('\n***** Valid states *****', end='')
    print('    obj:', end='')
    for i in range(valid_obj_limit):
        print('%4d' % i, end='')
    print()
    
    for state in valid_states:
        print(state, '       ', end='')
        h, aux_var_values = valid_states_hist[state]
        for obj in range(0, valid_obj_limit):
            if obj in h:
                print('%4d' % h[obj], end='')
            else:
                print('    ', end='')
        print(aux_var_values)
            

    print('\n***** Invalid states *****')
    for i in range(invalid_obj_limit):
        if i in invalid_states_hist:
            num_states = invalid_states_hist[i]
        else:
            num_states = 0
        print('objective value = %2d ; number of invalid states = %4d' % (i, num_states))


else:
    print(usage_message)
    sys.exit(1)
