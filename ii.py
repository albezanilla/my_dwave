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


def generate_valid_states(cube):
    V = set()
    for s in itertools.product([True, False], repeat=5):
        cube_copy = copy.copy(cube)
        apply_switches(cube_copy, s)
        valid_state = []
        valid_state += color_code[cube_copy['+X']]
        valid_state += color_code[cube_copy['+Z']]
        valid_state += color_code[cube_copy['-X']]
        valid_state += color_code[cube_copy['-Z']]
        V.add(tuple(valid_state))
    return V


def cube_configurations(ci):
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

    return variable_name_tuple, (generate_valid_states(cube))


def face_configurations(face):
    variable_name_tuple = [cube + '_' + face + '_' + bit for cube in 'ABCD' for bit in ['lo', 'hi']]
    valid_states = set()
    for t in itertools.product([0,1], repeat=8):
        L = [t[0] + 2*t[1], t[2] + 2*t[3], t[4] + 2*t[5], t[6] + 2*t[7]]
        L.sort()
        if L == [0, 1, 2, 3]:
            valid_states.add(t)
    return variable_name_tuple, valid_states


def print_valid_configurations(vars, states):
    for var in vars:
        print('  %8s' % var, end='')
    print()

    for var in vars:
        print('  %8s' % '--------', end='')
    print('')

    for state in states:
        for bit in state:
            print('  %8d' % bit, end='')
        print('')

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1][0:4] == 'cube':
            cube_index = int(sys.argv[1][4])
            variables, valid_states = cube_configurations(cube_index)
        else:
            face = sys.argv[1][0]
            variables, valid_states = face_configurations(face)
        print_valid_configurations(variables, valid_states)
        
    else:
        print('Usage: ii.py {cube1|cube2|cube3|cube4|up|down|front|back}')
        sys.exit(1)
