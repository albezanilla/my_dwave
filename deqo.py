import sympy
import itertools
import deqo_lower


def state_is_penalized_by_constraint(state, constraint):
    return all([True if constraint[i] is None else state[i] != constraint[i] for i in range(logical_vars)])


def state_is_not_penalized_by_constraint(state, constraint):
    return any([False if constraint[i] is None else state[i] == constraint[i] for i in range(logical_vars)])


def states_are_not_penalized_by_constraint(states, constraint):
    return all([state_is_not_penalized_by_constraint(state, constraint) for state in states])


def find_constraints_that_do_not_penalize_states(states):
    constraint_list = []
    for constraint in itertools.product([0, 1, None], repeat=logical_vars):
        if states_are_not_penalized_by_constraint(states, constraint):
            constraint_list.append(constraint)
    return constraint_list


def num_states_penalized_by_constraint(invalid_states, constraint):
    num_penalized = 0
    for state in invalid_states:
        if state_is_penalized_by_constraint(state, constraint):
            num_penalized += 1
    return num_penalized


def find_best_constraint(invalid_states, con_by_deg):
    max_penalized = 0
    for degree in range(logical_vars+1):
        for con in con_by_deg[degree]:
            penalized = num_states_penalized_by_constraint(invalid_states, con)
            if penalized > max_penalized:
                max_penalized = penalized
                max_con = con
    return max_penalized, max_con


def evaluate_state_with_constraints(state, constraints):
    val = 0
    for c in constraints:
        if state_is_penalized_by_constraint(state, c):
            val += 1
    return val


def compute_constraint_set(v_states, iv_states):

    cs = find_constraints_that_do_not_penalize_states(v_states)

    constraint_by_degree = {i: [] for i in range(logical_vars+1)}

    for constraint in cs:
        power = sum([0 if v == None else 1 for v in constraint])
        constraint_by_degree[power].append(constraint)

    for degree in constraint_by_degree.keys():
        constraint_by_degree[degree].sort(key=lambda T: [2 if v is None else v for v in T])

    constraint_set = set()

    while len(iv_states) > 0:
        p, c = find_best_constraint(iv_states, constraint_by_degree)
        constraint_set.add(c)
        penalized_states = set()
        for state in iv_states:
            if state_is_penalized_by_constraint(state, c):
                penalized_states.add(state)
        iv_states -= penalized_states

    return constraint_set


def make_hubo(sym_tuple, v_states):

    # Create the set of invalid states from the set of valid states:
    vars = len(sym_tuple)

    iv_states = set()
    for state in itertools.product([0,1], repeat=vars):
        if state not in v_states:
            iv_states.add(state)

    iv_states_return = iv_states.copy()
    
    cs = compute_constraint_set(v_states, iv_states)

    hubo = 0
    for c in cs:
        constraint_expr = 1
        for i, token in enumerate(c):
            if token == 0:
                constraint_expr *= sym_tuple[i]
            elif token == 1:
                constraint_expr *= (1 - sym_tuple[i])
        constraint_expr = sympy.expand(constraint_expr)
        hubo += constraint_expr

    return hubo, list(sym_tuple), iv_states_return


def product_rule(prod_var, x, y):
    return 3*prod_var - 2*prod_var*(x + y) + x*y


def fix_prod_param(hubo, qubo_with_param, v_states, sym_tuple, aux_tuple, pp):

    valid_state_objs = set()
    excited_state_objs = set()
    
    for state in itertools.product([0,1], repeat=logical_vars):
        substitutions = [(sym_tuple[i], state[i]) for i in range(logical_vars)]
        obj = hubo.subs(substitutions)
        if state in v_states:
            valid_state_objs.add(obj)
        else:
            excited_state_objs.add(obj)

    bound = min(excited_state_objs)
    
    all_vars = sym_tuple + aux_tuple
    prod_param = None
    for state in itertools.product([0,1], repeat=len(all_vars)):
        substitutions = [(all_vars[i], state[i]) for i in range(len(all_vars))]
        obj = qubo_with_param.subs(substitutions)
        final_vars = obj.as_coefficients_dict()
        if pp in final_vars.keys():
            pp_coeff = final_vars[pp]
            constant = obj.subs([(pp, 0)])
            prod_param_bound = (bound - constant) / pp_coeff
            if prod_param is None or prod_param_bound > prod_param:
                prod_param = prod_param_bound

    substituted_qubo = qubo_with_param.subs([(pp, prod_param)])
    return substituted_qubo


def make_qubo(sym_tuple, v_states, aux_var_basename='aux'):
    # Check that the valid states all have the correct number of booleans:
    global logical_vars
    logical_vars = len(sym_tuple)
    state_vars = [len(state) for state in v_states]
    if max(state_vars) != logical_vars or min(state_vars) != logical_vars:
        print('make_qubo: not all states have the correct number of booleans')
        raise ValueError

    # Introduce a symbol for the Lagrange parameter which controls the
    # strength of the product constraint QUBOs:
    prod_param = sympy.symbols('prod_param')

    hubo, sym_list, iv_states = make_hubo(sym_tuple, v_states)
    poly_list, replacement_list = deqo_lower.hubo_to_qubo(hubo, aux_var_basename)
    qubo = poly_list[-1]
    aux_list = []
    for replacement in replacement_list:
        prod_var, pair = replacement
        x, y = pair
        product_qubo = product_rule(prod_var, x, y)
        qubo += prod_param * product_qubo
        aux_list.append(prod_var)

    if len(replacement_list) > 0:
        qubo = fix_prod_param(hubo, qubo, v_states, sym_tuple, tuple(aux_list), prod_param)
        
    return sympy.expand(qubo), replacement_list


def all_vars_from_poly(poly):
    vars = set()
    d = poly.as_coefficients_dict()
    for k in d.keys():
        var_dict = k.as_powers_dict()
        var_set = {var for var in var_dict.keys() if type(var) is sympy.core.symbol.Symbol}
        vars |= var_set
    return vars

    
def check_qubo(sym_tuple, v_states, qubo):
    # Get the set of all variables in the qubo and subtract from it
    # the set of the logical variables to obtain the set of auxiliary
    # variables.
    all_vars = all_vars_from_poly(qubo)
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
