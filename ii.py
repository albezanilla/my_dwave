import sys
import copy
import itertools


cube1 = {'-Y' : 'green', '+Z' : 'green', '+Y' : 'green', '-Z' : 'red'  , '-X' : 'white', '+X' : 'blue' }
cube2 = {'-Y' : 'red'  , '+Z' : 'white', '+Y' : 'red'  , '-Z' : 'blue' , '-X' : 'blue' , '+X' : 'green'}
cube3 = {'-Y' : 'green', '+Z' : 'blue' , '+Y' : 'white', '-Z' : 'green', '-X' : 'red'  , '+X' : 'white'}
cube4 = {'-Y' : 'white', '+Z' : 'red'  , '+Y' : 'blue' , '-Z' : 'white', '-X' : 'green', '+X' : 'red'  }

# In the following encoding of colors as bits, the first value is 'lo' and the second is 'hi':

color_code = {'red' : [0, 0], 'white' : [0, 1], 'blue' : [1, 0], 'green' : [1, 1]}

def bits_to_color(lo, hi):
    for color, bits in color_code.items():
        if [lo, hi] == bits:
            return color


def rotation_by_pi_over_2_around_x(cube):
    color_A = cube['+Y']
    color_B = cube['+Z']
    color_C = cube['-Y']
    color_D = cube['-Z']
    cube['+Y'] = color_D
    cube['+Z'] = color_A
    cube['-Y'] = color_B
    cube['-Z'] = color_C


def rotation_by_pi_around_x(cube):
    rotation_by_pi_over_2_around_x(cube)
    rotation_by_pi_over_2_around_x(cube)


def rotation_by_pi_over_2_around_z(cube):
    color_A = cube['+X']
    color_B = cube['+Y']
    color_C = cube['-X']
    color_D = cube['-Y']
    cube['+X'] = color_D
    cube['+Y'] = color_A
    cube['-X'] = color_B
    cube['-Y'] = color_C


def rotation_by_pi_around_z(cube):
    rotation_by_pi_over_2_around_z(cube)
    rotation_by_pi_over_2_around_z(cube)


def apply_switches(cube, switches):
    if switches[0]:
        rotation_by_pi_over_2_around_z(cube)
    if switches[1]:
        rotation_by_pi_around_x(cube)
    if switches[2]:
        rotation_by_pi_over_2_around_x(cube)
    if switches[3]:
        rotation_by_pi_around_z(cube)
    if switches[4]:
        rotation_by_pi_over_2_around_z(cube)


def interpret_switches(switches):
    rotations = []
    if switches[0]:
        rotations.append('Z:pi/2')
    if switches[1]:
        rotations.append('X:pi')
    if switches[2]:
        rotations.append('X:pi/2')
    if switches[3]:
        rotations.append('Z:pi')
    if switches[4]:
        rotations.append('Z:pi/2')
    return rotations
        
    
def generate_valid_states(cube):
    rotations_for_valid_states = dict()
    for s in itertools.product([True, False], repeat=5):
        cube_copy = copy.copy(cube)
        apply_switches(cube_copy, s)
        valid_state = []
        valid_state += color_code[cube_copy['+X']]
        valid_state += color_code[cube_copy['+Z']]
        valid_state += color_code[cube_copy['-X']]
        valid_state += color_code[cube_copy['-Z']]
        if tuple(valid_state) in rotations_for_valid_states:
            rotations_for_valid_states[tuple(valid_state)].append(s)
        else:
            rotations_for_valid_states[tuple(valid_state)] = [s]
    return rotations_for_valid_states


def cube_configurations(ci, include_rotations=False):
    cube_names = 'ABCD'
    
    variable_name_tuple = [cube_names[ci-1] + '_' + face + '_' + bit for face in 'fubd' for bit in ['lo', 'hi']]

    if ci == 1:
        cube = cube1
    elif ci == 2:
        cube = cube2
    elif ci == 3:
        cube = cube3
    elif ci == 4:
        cube = cube4
    else:
        print('cube must be 1, 2, 3 or 4')
        quit()

    valid_state_rotations = generate_valid_states(cube)

    if include_rotations:
        return variable_name_tuple, valid_state_rotations
    else:
        return variable_name_tuple, set(valid_state_rotations.keys())


def face_configurations(face):
    variable_name_tuple = [cube + '_' + face + '_' + bit for cube in 'ABCD' for bit in ['lo', 'hi']]
    valid_states = set()
    for t in itertools.product([0,1], repeat=8):
        L = [t[0] + 2*t[1], t[2] + 2*t[3], t[4] + 2*t[5], t[6] + 2*t[7]]
        L.sort()
        if L == [0, 1, 2, 3]:
            valid_states.add(t)
    return variable_name_tuple, valid_states


def print_valid_configurations(vars, states, rotations=None, output='colors'):

    # Print the list of variables to be displayed:

    if output in {'bits', 'both'}:
        for var in vars:
            print('  %8s' % var, end='')

    if output in {'colors', 'both'}:
        for var in vars:
            if var.endswith('_hi'):
                print('  %8s' % var.replace('_hi', ''), end='')

    print()


    # Print a separator line of dashes:

    if output in {'bits', 'both'}:
        for var in vars:
            print('  %8s' % '--------', end='')

    if output in {'colors', 'both'}:
        for var in vars:
            if var.endswith('_hi'):
                print('  %8s' % '--------', end='')

    print()


    # Print the states:

    for state in states:
        if output in {'bits', 'both'}:
            for bit in state:
                print('  %8d' % bit, end='')

        if output in {'colors', 'both'}:
            colors = [bits_to_color(state[i], state[i+1]) for i in range(0, 8, 2)]
            for color in colors:
                print('  %8s' % color, end='')

        if rotations is not None:
            for rotation in rotations[state]:
                print(' ', interpret_switches(rotation), end='')

        print()



if __name__ == '__main__':
    try:
        sys.argv.remove('-rotations')
        do_rotations = True
    except ValueError:
        do_rotations = False

    output = 'bits'
    
    try:
        sys.argv.remove('-colors')
        output = 'colors'
    except ValueError:
        pass
    
    try:
        sys.argv.remove('-both')
        output = 'both'
    except ValueError:
        pass
    
    if do_rotations and sys.argv[1][0:4] != 'cube':
        print('error: optional argument -rotations is only valid with cube1...cube4')
        sys.exit(1)
        
    if len(sys.argv) == 2:
        if sys.argv[1][0:4] == 'cube':
            cube_index = int(sys.argv[1][4])
            if do_rotations:
                variables, valid_state_rotations = cube_configurations(cube_index, include_rotations=True)
            else:
                variables, valid_states = cube_configurations(cube_index)
        else:
            face = sys.argv[1][0]
            variables, valid_states = face_configurations(face)

        if do_rotations:
            print_valid_configurations(variables, set(valid_state_rotations.keys()), valid_state_rotations, output=output)
        else:
            print_valid_configurations(variables, valid_states, output=output)
        
    else:
        print('Usage: ii.py [-rotations] [-colors|-both] {cube1|cube2|cube3|cube4|up|down|front|back} ')
        sys.exit(1)
