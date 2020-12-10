import sympy_util
import itertools

def check_qubo(sym_tuple, v_states, qubo):
    # Get the set of all variables in the qubo and subtract from it
    # the set of the logical variables to obtain the set of auxiliary
    # variables.
    all_vars = sympy_util.poly_vars(qubo)
    aux_vars = list(all_vars - set(sym_tuple))

    # For each setting of the logical variables, compute the minimum
    # objective for all possible settings of the auxiliary variables.
    # Save this into the all_obj dict:
    all_obj = dict()
    for state in itertools.product([0,1], repeat=len(sym_tuple)):
        substitutions = [(sym_tuple[i], state[i]) for i in range(len(sym_tuple))]
        min_obj = None
        for aux_state in itertools.product([0,1], repeat=len(aux_vars)):
            aux_substitutions = [(aux_vars[i], aux_state[i]) for i in range(len(aux_vars))]
            all_substitutions = substitutions + aux_substitutions
            obj = qubo.subs(all_substitutions)
            if min_obj is None or obj < min_obj:
                min_obj = obj
        all_obj[tuple(state)] = min_obj

    # Iterate over all logical states (skipping the auxiliary
    # variables).  For valid states, compute the minimum and maximum
    # objective seen.  For invalid states, compute the minimum
    # objective seen.
    min_valid_obj = None
    max_valid_obj = None
    min_invalid_obj = None
    for state in itertools.product([0,1], repeat=len(sym_tuple)):
        obj = all_obj[state]
        if state in v_states:
            if min_valid_obj is None or obj < min_valid_obj:
               min_valid_obj = obj
            if max_valid_obj is None or obj > max_valid_obj:
               max_valid_obj = obj
        else:
            if min_invalid_obj is None or obj < min_invalid_obj:
                min_invalid_obj = obj

    return min_valid_obj, max_valid_obj, min_invalid_obj
