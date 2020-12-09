import itertools
import penaltymodel.mip
import dimod
import networkx as nx
import sys
import ii
import sympy
import sympy_util
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

    symbol_names = ['spin_' + name for name in symbol_names]
    aux_names = ['spin_' + name for name in aux_names]
    all_names = symbol_names + aux_names
    aux_names = [name.replace('spin_', '') for name in aux_names]
    num_vars = len(all_names)
    graph = nx.complete_graph(all_names)

    feasible_configurations = set()
    for bool_state in valid_states:
        spin_state = tuple( (1 - 2*bool_state[i] for i in range(8)) )
        feasible_configurations.add(spin_state)
        
    # Generate BQM over Ising states:
    bqm, gap, aux = penaltymodel.mip.generation.generate_bqm(graph,
                                                             feasible_configurations,
                                                             symbol_names,
                                                             max_variables=num_vars,
                                                             return_auxiliary=True)

    # Map each string name (logical and auxiliary) to a Sympy symbol:
    symbols = dict()
    for name in all_names:
        symbol = sympy.symbols(name)
        symbols[name] = symbol

    # Iterate over the linear and quadratic terms in the BQM and for
    # each term, build a corresponding Sympy term and add it to
    # subising.
    subising = 0
    for var, weight in bqm.linear.items():
        subising += weight * symbols[var]

    for (var1, var2), strength in bqm.quadratic.items():
        subising += strength * symbols[var1] * symbols[var2]

    # Now that we have built the Ising model, convert it to a QUBO.
    # First, list all variables in the Ising model:
    all_vars = sympy_util.poly_vars(subising)

    # Build a dict that maps spin variables to boolean variables:
    spin_to_qubo = dict()
    for var in all_vars:
        spin_to_qubo[var] = 1 - 2*sympy.symbols(var.name.replace('spin_', ''))

    # Apply the dict of variable substitutions to the Ising model to
    # generate the QUBO:
    subqubo = subising.subs(spin_to_qubo)

    # Expand the QUBO so we are left with a sum of products:
    subqubo = subqubo.expand()

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
