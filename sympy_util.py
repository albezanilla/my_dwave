from sympy.core.symbol import Symbol

def poly_vars(poly):
    vars = set()
    d = poly.as_coefficients_dict()
    for k in d.keys():
        var_dict = k.as_powers_dict()
        var_set = {var for var in var_dict.keys() if type(var) is Symbol}
        vars |= var_set
    return vars
