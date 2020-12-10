import sys
import sympy
import itertools
import deqo
import ii
import pickle

valid_args = {'cube1', 'cube2', 'cube3', 'cube4', 'up', 'down', 'front', 'back'}
usage_message = 'Usage: subqubo_deqo.py {cube1|cube2|cube3|cube4|up|down|front|back}'

if len(sys.argv) == 2:
    arg = sys.argv[1]
    if arg not in valid_args:
        print(usage_message)
        sys.exit(1)

    if arg[0:4] == 'cube':
        cube_num = int(arg[4])
        cube_vars, valid_states = ii.cube_configurations(cube_num)
        symbols = tuple(sympy.symbols(cube_vars))
        aux = 'ABCD'[cube_num - 1] + '_aux_'

    else:
        face = arg[0]
        face_vars, valid_states = ii.face_configurations(face)
        symbols = tuple(sympy.symbols(face_vars))
        aux = face + '_aux_'

    print('\n**************** Valid states ****************\n')
    for symbol in symbols:
        print('  %8s' % symbol, end='')
    print('')
    
    for symbol in symbols:
        print('  %8s' % '--------', end='')
    print('')
    
    for state in valid_states:
        for bit in state:
            print('  %8d' % bit, end='')
        print('')

    Q, A = deqo.make_qubo(symbols, valid_states, aux_var_basename=aux)

    print('\n**************** QUBO for %s ****************\n' % arg)
    print(Q)

    print('\n**************** Auxiliary variables ****************\n')
    print(A)

    filename = '%s.deqo.pickle' % (arg)
    with open(filename, 'wb') as f:
        pickle.dump(Q, f, pickle.HIGHEST_PROTOCOL)

else:
    print(usage_message)
    sys.exit(1)
