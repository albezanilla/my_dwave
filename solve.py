# This is a recursive depth-first tree search which finds solutions to
# the Instant Insanity puzzle - purely classically.  It relies on the
# ii module to obtain the eight constraints.  Each constraint lists
# the valid settings of a subset of variables for the complete
# problem.  This program finds a setting for the entire set of 32
# variables such that each constraint is satisfied.
#
# The solutions can be printed in one of three ways: as bits, as
# colors or as both.  In the first mode, the values of all 32 bits in
# each solution are displayed.  In the second mode, pairs of the 32
# variables are decoded to represent one of four colors and the 16
# colors are displayed.  In the third mode, both the bit
# and color representations are displayed one above the other
# to show the correspondence between bits and colors.
#
# Without any command line argument, both the bit and color
# representation are displayed.  Optionally, specify a single command
# line argument of 'bits', 'colors' or 'both' to select the display
# format.
#
# This program can also write out a pickle file containing the answers
# to the puzzle.  To do this, edit the program and set the
# write_answers variable True and run the program.  When write_answers
# is False, no pickle file will be written.  The format of the pickle
# file is a list of length eight - each entry in the list corresponds
# to a single answer to the puzzle.  Each entry is a dict mapping the
# 32 basic variables over which the puzzle is defined to a 0/1 value.
# The 32 basic variables appear as strings.  The strings are of this
# form:
#           {A|B|C|D}_{u|d|f|b}_{lo|hi}

write_answers = False
filename = 'solve.pickle'

import ii
import sys
import pickle

usage_message = 'solve.py [bits|colors|both]'

if len(sys.argv) == 1:
    answer_format = 'both'
elif sys.argv[1] in {'bits', 'colors', 'both'}:
    answer_format = sys.argv[1]
else:
    print(usage_message)
    sys.exit(1)

if write_answers:
    answers = []

def print_solution(var_vals):

    if write_answers:
        answers.append(var_vals.copy())
    
    if answer_format in {'bits', 'both'}:
        print('%s Solution (bits) %s' % ('*' * 40, '*' * 40))
        for face in 'fdbu':
            for cube in 'ABCD':
                for bit in ('hi', 'lo'):
                    var = cube + '_' + face + '_' + bit
                    val = var_vals[var]
                    print('%10s=%d' % (var, val), end='')
            print()

    if answer_format in {'colors', 'both'}:
        num_stars = 40 if answer_format == 'both' else 8
        print('%s Solution (colors) %s' % ('*' * num_stars, '*' * (num_stars - 2)))
        cube_face_colors = { cube + '_' + face : '' for cube in 'ABCD' for face in 'udfb'}
        for cube_face in cube_face_colors.keys():
            color = ii.bits_to_color(var_vals[cube_face + '_lo'], var_vals[cube_face + '_hi'])
            cube_face_colors[cube_face] = color
        for face in 'fdbu':
            for cube in 'ABCD':
                if answer_format == 'both':
                    spacing = '%8s' if cube == 'A' else '%16s'
                    print(spacing % '', end='')
                print('%4s_%s=%s' % (cube, face, cube_face_colors[cube + '_' + face][0].upper()), end='')
            print()

    print()
    

def get_constraints():
    constraints = []

    for cube_num, face in list(zip(range(1,5), 'udfb')):

        cube_vars, cube_states = ii.cube_configurations(cube_num)
        constraints.append( (cube_vars, cube_states) )

        face_vars, face_states = ii.face_configurations(face)
        constraints.append( (face_vars, face_states) )

    return constraints


def check_consistency(var_vals, variables, state):
    checks = [var_vals[var] == val if var in var_vals else True for var, val in zip(variables, state)]
    if all(checks):
        newly_set_vars = set()
        for var, val in zip(variables, state):
            if var not in var_vals:
                newly_set_vars.add(var)
                var_vals[var] = val
        return True, newly_set_vars
    else:
        return False, None
    

def recurse(cons, var_vals, level):

    if level == len(cons):
        print_solution(var_vals)
        return

    variables, valid_states = cons[level]

    for state in valid_states:
        consistent, fixed_variables = check_consistency(var_vals, variables, state)
        if consistent:
            recurse(cons, var_vals, level+1)
            for var in fixed_variables:
                del var_vals[var]


constraints = get_constraints()

variable_values = dict()

recurse(constraints, variable_values, 0)

if write_answers:
    with open(filename, 'wb') as f:
        pickle.dump(answers, f, pickle.HIGHEST_PROTOCOL)
