# This utility tweaks the QUBOs stored as pickle files.  The
# motivation for this comes from Ocean's generated QUBOs - they
# generally have a minima at an objective value which is different
# from zero.  Additionally, it is useful to adjust the gap between the
# ground state and first excited state to a desired value.  Also, it
# is desirable to convert the QUBO coefficients to integer values.
# This utility can accomplish that.  Plus, it is a useful display
# utility for examining the contents of a pickled QUBO.
#
# The arguments each represent actions which are executed in the order
# in which they appear in the command line.  Generally the first
# action will be '-in', which causes the QUBO to be read into memory.
# It is frequently convenient to then use the '-display' action so
# that the QUBO is printed.  Other actions may follow.  If it is
# desired to write out the QUBO, the final action will generally be
# '-out'.
#
# Use the '-h' action to display the help message which lists the
# possible actions.
#
# This utility can also be used to sum together multiple QUBOs using
# the '-accumulate' action.
#
# Could we implement variable renaming in here also?  That would allow
# us to get rid of rename_subqubo.py.


import pickle
import sympy
import sys

usage_message = '''
Usage: tweak_qubo.py [action1 [action2 [action3 ...]]]

Supported actions:

    -help
    -in:<filename>
    -display
    -out:<filename>
    -add:<x>
    -mul:<x>
    -round
    -accumulate:<filename>

'''

actions = sys.argv[1:]

valid_actions = {'-help', '-in', '-out', '-display', '-add', '-mul',
                 '-round', '-accumulate'}

action_check = [action.split(':')[0] in valid_actions for action in actions]

if all(action_check) is not True:
    print('error: one or more actions are not valid')
    sys.exit(1)

qubo = 0

for action in actions:

    if action.startswith('-help'):
        print(usage_message)

    elif action.startswith('-in'):
        filename = action.replace('-in:', '')
        try:
            with open(filename, 'rb') as f:
                qubo = pickle.load(f)
        except FileNotFoundError:
            print('error: file "%s" does not exist' % filename)
            sys.exit(1)

    elif action.startswith('-display'):
        print(qubo)
        
    elif action.startswith('-out'):
        filename = action.replace('-out:', '')
        with open(filename, 'wb') as f:
            pickle.dump(qubo, f, pickle.HIGHEST_PROTOCOL)

    elif action.startswith('-add'):
        val = float(action.replace('-add:', ''))
        qubo += val
        
    elif action.startswith('-mul'):
        val = float(action.replace('-mul:', ''))
        qubo *= val
        
    elif action.startswith('-round'):
        new_qubo = 0
        d = qubo.as_coefficients_dict()
        for key, val in d.items():
            new_qubo += key * int(val)
        qubo = new_qubo
        
    elif action.startswith('-accumulate'):
        filename = action.replace('-accumulate:', '')
        try:
            with open(filename, 'rb') as f:
                subqubo = pickle.load(f)
        except FileNotFoundError:
            print('error: file "%s" does not exist' % filename)
            sys.exit(1)
        qubo += subqubo

    else:
        print('error: unrecognized action')
        sys.exit(1)
