import itertools
import penaltymodel.mip
import dimod
import networkx as nx
import sys
import ii
import sympy
import pickle

valid_args = {'cube1', 'cube2', 'cube3', 'cube4', 'up', 'down', 'front', 'back'}
usage_message = 'Usage: subqubo_ocean.py {cube1|cube2|cube3|cube4|up|down|front|back} -aux NNN'

if len(sys.argv) == 4:
    arg = sys.argv[1]
    if arg not in valid_args:
        print(usage_message)
        sys.exit(1)

    if sys.argv[2] != '-aux':
        print(usage_message)
        sys.exit(1)

    try:
        num_aux_vars = int(sys.argv[3])
    except ValueError:
        print('Error: argument following "-aux" must be an integer')
        sys.exit(1)
    
    if arg[0:4] == 'cube':
        cube_num = int(arg[4])
        symbol_names, valid_states = ii.cube_configurations(cube_num)
        aux_names = ['ABCD'[cube_num - 1] + '_aux_' + '%d' % i for i in range(num_aux_vars)]

    else:
        face = arg[0]
        symbol_names, valid_states = ii.face_configurations(face)
        aux_names = [face + '_aux_' + '%d' % i for i in range(num_aux_vars)]

    print('\n**************** valid states ****************\n')
    for symbol_name in symbol_names:
        print('  %8s' % symbol_name, end='')
    print('')
    
    for symbol_name in symbol_names:
        print('  %8s' % '--------', end='')
    print('')
    
    for state in valid_states:
        for bit in state:
            print('  %8d' % bit, end='')
        print('')

    all_names = symbol_names + aux_names
    num_vars = len(all_names)
    graph = nx.Graph()
    for var in all_names:
        graph.add_node(var)
    for edge in itertools.combinations(all_names, 2):
        graph.add_edge(edge[0], edge[1])

    feasible_configurations = set()
    for bool_state in valid_states:
        spin_state = tuple( (1 - 2*bool_state[i] for i in range(8)) )
        feasible_configurations.add(spin_state)
        
    # Generate BQM:
    bqm, gap, aux = penaltymodel.mip.generation.generate_bqm(graph,
                                                             feasible_configurations,
                                                             symbol_names,
                                                             max_variables=num_vars,
                                                             return_auxiliary=True)

    symbols = dict()
    for name in all_names:
        symbol = sympy.symbols(name)
        symbols[name] = symbol

    subqubo = 0
    for var, weight in bqm.linear.items():
        subqubo += weight * symbols[var]

    for (var1, var2), strength in bqm.quadratic.items():
        subqubo += strength * symbols[var1] * symbols[var2]

    print('\n**************** QUBO for %s ****************\n' % arg)
    print(subqubo)

    print('\n**************** Auxiliary variables ****************\n')
    print(aux_names)

    filename = '%s.ocean.pickle' % (sys.argv[1])
    with open(filename, 'wb') as f:
        pickle.dump(subqubo, f, pickle.HIGHEST_PROTOCOL)

    
else:
    print(usage_message)
    sys.exit(1)
