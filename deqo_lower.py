import sympy
from itertools import combinations


def hubo_to_qubo(poly, aux, reduction_limit=12):

    # The zeroth element of the poly_list is the original HUBO:
    poly_list = [poly]

    # Each variable pair replacement is recorded as a tuple in this
    # list.  The first element of the tuple is the new variable and
    # the second element is a set consisting of the two variables
    # whose product is replaced by the new variable:
    replacement_list = []

    # Call the lower() function until it returns None for the variable
    # pair replacement.  This means that the polynomial is a QUBO.  In
    # this case, return the list of reduced polynomials and the list
    # of variable pair replacements:
    
    for i in range(reduction_limit):
        aux_var = aux + ('%d' % i)
        poly, replacement = lower(poly_list[-1], aux_var)
        if replacement is None:
            return poly_list, replacement_list
        else:
            poly_list.append(poly)
            replacement_list.append(replacement)

    # If we reach this point, the maximum number of reductions has
    # been applied and the HUBO has not yet been reduced to a QUBO:
    print('deqo.hubo_to_qubo() : reduction limit (%d) has been reached' % reduction_limit)
    raise ValueError


def lower(poly, aux_var_name):

    # Create a set containing all the variables appearing in polynomial:
    vars = set()

    # Convert poly into a dict keyed by monomials and whose values are coefficients:
    d = poly.as_coefficients_dict()

    # Iterate over the keys in d - these are the monomials appearing in poly.
    # For each one, convert the monomial into a dict keyed by
    # variables and whose values are the exponents of each variable.
    # Since we are working with boolean variables, the exponents will
    # always be 1 and so we can convert the dict to a set.

    # Form the union of these sets across all terms - this gives us
    # the complete set of variables appearing in expr.
    # Also, keep track of the maximum degree of all terms.
    
    max_degree = 0
    
    for k in d.keys():
        var_dict = k.as_powers_dict()
        var_set = {var for var in var_dict.keys() if type(var) is sympy.core.symbol.Symbol}
        vars |= var_set
        if len(var_set) > max_degree:
            max_degree = len(var_set)

    # If the maximum degree of any term is two or less, poly is
    # already a QUBO and we have no more work to do.  Return the
    # polynomial we were called with and None.
    
    if max_degree <= 2:
        return poly, None
    
    # Iterate over all pairs of variables appearing in the expression.
    # For each one, compute the total amount of degree reduction
    # if we replaced that variable pair by a new product variable.
    # Find the variable pair that results in the largest reduction.
    
    best_reduction = 0

    for var_pair in combinations(vars, 2):
        set_var_pair = set(var_pair)
        reduction = 0
        for k in d.keys():
            var_dict = k.as_powers_dict()
            var_set = {var for var in var_dict.keys() if type(var) is sympy.core.symbol.Symbol}
            if len(var_set) >= 3 and set_var_pair <= var_set:
                reduction += 1
        if reduction > best_reduction:
            best_reduction = reduction
            best_var_pair = set_var_pair

    # Now that we've determined the best variable pair to replace with
    # a product variable, iterate over the key/value pairs
    # representing the original expr.  For any term which contains
    # the best variable pair, replace it with the reduced term.

    reduced_poly = 0

    new_var = sympy.symbols(aux_var_name)
    
    for monomial, coeff in d.items():
        var_dict = monomial.as_powers_dict()
        var_set = {var for var in var_dict.keys() if type(var) is sympy.core.symbol.Symbol}
        if best_var_pair <= var_set:
            var_set = var_set - best_var_pair
            this_term = coeff * new_var
            for var in var_set:
                this_term *= var
            reduced_poly += this_term
        else:
            reduced_poly += coeff * monomial

    return reduced_poly, (new_var, best_var_pair)
