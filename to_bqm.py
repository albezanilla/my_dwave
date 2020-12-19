import pickle
import sympy
import sympy_util
import dimod

in_filename = 'total.pickle'
out_filename = 'bqm.pickle'

try:
    with open(in_filename, 'rb') as f:
        qubo = pickle.load(f)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)

Q = {}

coefficients_dict = qubo.as_coefficients_dict()

for vars, coeff in coefficients_dict.items():
    var_dict = vars.as_powers_dict()
    if len(var_dict) == 1:
        var, = list(var_dict.keys())
        if hasattr(var, 'name'):
            Q[(var.name, var.name)] = coeff
            print('LINEAR TERM: var=%s coeff=%s' % (var.name, str(coeff)))
        else:
            print('CONSTANT TERM: %s coeff=%s' % (var, str(coeff)))
    elif len(var_dict) == 2:
        var1, var2 = list(var_dict.keys())
        Q[(var1.name, var2.name)] = coeff
        print('QUADRATIC TERM: var1=%s var2=%s coeff=%s' % (var1.name, var2.name, str(coeff)))

bqm = dimod.BinaryQuadraticModel.from_qubo(Q)

try:
    with open(out_filename, 'wb') as f:
        pickle.dump(bqm, f, pickle.HIGHEST_PROTOCOL)
except FileNotFoundError:
    print('error: file "%s" does not exist' % filename)
    sys.exit(1)
